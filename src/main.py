# main.py
from fastapi import Depends, FastAPI, Header, HTTPException
from pony.orm import db_session, select

from api.routers import users
from api.models.base import db


app = FastAPI()

db.bind('sqlite', 'example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

app.include_router(users.router)


@app.get("/")
async def greeting():
    '''
    Mensaje de recibida 
    '''
    return {"message": "Hello World"}

# if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
