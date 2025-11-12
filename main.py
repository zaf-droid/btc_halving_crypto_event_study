import uvicorn
from fastapi import FastAPI
from routers import users
from db.database import create_db_and_tables
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)