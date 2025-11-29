import uvicorn
from fastapi import FastAPI
from routers import users, ohlc, event_study
from db.database import create_db_and_tables
from services.utils.create_default_data import insert_btc_halving_dates

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    insert_btc_halving_dates()

app.include_router(users.router)
app.include_router(ohlc.router)
app.include_router(event_study.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
