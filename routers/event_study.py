from fastapi import APIRouter, Depends, Query
from schemas.query_parameters import EventParams
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from core.dependencies import get_session
from db.models import Events, OHLC
from schemas.query_parameters import EventStudyParams
from services.crud.event import create_event
from services.utils.validators import *
from services.crud.event import get_event_data

router = APIRouter(prefix="/event-study", tags=["event-study"])

@router.post('/new', response_model=Events, status_code=201)
async def create_event_study(params: EventParams, session: Annotated[Session, Depends(get_session)]):
    event = create_event(session=session, event_params=params)
    return event

@router.get('/data')
async def get_event_study_results(event_study_params: Annotated[EventStudyParams, Query()],
                                  session: Annotated[Session, Depends(get_session)],
                                  ):
    validate_value_in_db(session=session,
                         model=Events,
                         column=Events.event_name,
                         value=event_study_params.event_name)

    validate_pairs_in_db(session=session,
                         model=OHLC,
                         pairs={OHLC.base_currency: event_study_params.base_currency,
                                OHLC.quote_currency: event_study_params.quote_currency,
                                OHLC.interval: event_study_params.window_unit}
                         )
    event_days_list = session.exec(
        select(Events.timestamp).where(Events.event_name == event_study_params.event_name)
    ).all()

    data = get_event_data(session=session,
                          window_after_event=event_study_params.window_after_event,
                          window_before_event=event_study_params.window_before_event,
                          window_unit=event_study_params.window_unit,
                          base_currency=event_study_params.base_currency,
                          quote_currency=event_study_params.quote_currency,
                          metric=event_study_params.metric,
                          event_days_list=event_days_list)
    return jsonable_encoder(data)

