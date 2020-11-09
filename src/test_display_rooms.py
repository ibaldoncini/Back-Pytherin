from os import name
from fastapi.applications import FastAPI
from pony.orm.core import get
from api.routers.hub_endpoints import get_rooms
from api.routers.room_endpoints import *
from fastapi.testclient import TestClient
from main import app
from pony.orm import db_session, commit
from api.models.base import DB_User
from random import randint
from classes.room import Room

#from test_room_create import test_happy_path


client = TestClient(app)
head = ""

def create_and_login(email: str):
    client.post(
        "/users/register",
        json={
            "username": email.split('@')[0],
            "email": email,
            "password": "Heladera65",
            "icon": "string",
        })
    response_login = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": email,
            "password": "Heladera65",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response_login.status_code == 200
    rta: dict = response_login.json()
    token: str = rta["access_token"]
    token_type: str = "Bearer "
    head: str = token_type + token
    with db_session:
        try:
            user = DB_User.get(email=email)
            user.set(email_confirmed=True)
            commit()
        except:
            pass

    print(email + " " + head)

    return {"accept": "application/json", "Authorization": head}


def join(header, room_name: str):
    client.get(
        f"/room/join/{room_name}",
        headers=header,
    )


owner = create_and_login("room_owner@email.com")
p1 = create_and_login("player1@email.com")
p2 = create_and_login("player2@email.com")
p3 = create_and_login("player3@email.com")
p4 = create_and_login("player4@email.com")


def create_room(name,max_players):
  print(head)
  response = client.post(
      "/room/new",
      headers=owner,
      json={"name": name, "max_players": max_players}
  )
  #assert response.status_code == 201
  #assert response.json() == {
   #   "message": "Room created successfully"}

players = [owner,p1,p2,p3,p4]


def join_several_players (room,n):
  if n > len(players):
    return
  count = 0
  for p in players:
    if count == n:
      break
    join(p,room)
    count += 1


def create_several_rooms (n):
  for i in range (n):
    max_p = randint(5,10)
    room_name = "Pytherin" + str(i)
    create_room(room_name,max_p)

#TODO test if the match still appearing even if it started
#hint: that should not happen
def main ():
  print(get_rooms())
  N_ROOMS = 5
  create_several_rooms(N_ROOMS)
  rooms = get_rooms()
  print("Rooms: " + rooms.__str__())
  real_rooms = rooms.get("message")
  room_names = []
  for room in real_rooms:
    room_names.append(room.get("name"))
  
  for i in range (0,N_ROOMS):
    n_players = randint(1,4)
    join_several_players(room_names[i],n_players)

  print("Rooms with people " + get_rooms().__str__())

main()