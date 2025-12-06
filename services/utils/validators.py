from fastapi import HTTPException
from sqlmodel import Session, select, and_

def validate_value_in_db(session: Session, model, column, value):
    exists = session.exec(
        select(model).where(column == value)
    ).first()

    if not exists:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value: '{value}' does not exist in the database column {column}."
        )

def validate_pairs_in_db(session: Session, model, pairs: dict):

    conditions = [ column == value for column, value in pairs.items() ]

    row = session.exec(
        select(model).where(and_(*conditions))
    ).first()

    if not row:
        details = ", ".join([ f"{column.key}='{value}'" for column, value in pairs.items() ])
        raise HTTPException(
            status_code=400,
            detail=f"No record found matching all of: {details}"
        )
