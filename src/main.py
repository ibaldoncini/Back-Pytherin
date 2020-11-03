# main.py
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from api.routers import users, room_endpoints
from api.routers import privileged
from api.models.base import db
from api.handlers.pass_handler import *
from api.handlers.authentication import verify_token


app = FastAPI()


db.bind('sqlite', 'example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


app.include_router(users.router)
app.include_router(room_endpoints.router, dependencies=[Depends(verify_token)])
# en el siguiente router, se encuentran algunas funciones que sirven para
# testear el correcto funcionamiento de los tokens, pues los endpoints
# que estan tienen como dependencia la funcion verify_token definida mas arriba
app.include_router(privileged.router, dependencies=[Depends(verify_token)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
