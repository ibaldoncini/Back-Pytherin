# main.py
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from api.routers import users,room_endpoints,user_info,hub_endpoints
from api.models.base import db
from api.handlers.authentication import verify_token


app = FastAPI()


db.bind('sqlite', 'example.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


app.include_router(users.router)
app.include_router(room_endpoints.router, dependencies=[Depends(verify_token)])
app.include_router(user_info.router, dependencies=[Depends(verify_token)])
app.include_router(hub_endpoints.router,dependencies=[Depends(verify_token)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
