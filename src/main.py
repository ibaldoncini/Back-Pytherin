
from fastapi import FastAPI

from api.routers import users

from api.models.base import db


app = FastAPI()

db.bind('sqlite','example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

app.include_router(users.router)

@app.get("/")
async def greeting():
  return {"message": "Hello World"}