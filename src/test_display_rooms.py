from api.routers.hub_endpoints import get_rooms
from api.routers.room_endpoints import *
from fastapi.testclient import TestClient
from test_main import test_app
from random import randint
from api.routers.room_endpoints import hub
from test_setup import join,create as create_room,start_game,p

client = TestClient(test_app)

#p = register_and_login()

owner = p[0]
p1 = p[1]
p2 = p[2]
p3 = p[3]
p4 = p[4]


def join_several_players (room,n):
  if n > len(p):
    return
  count = 0
  for player in p:
    if count == n:
      break
    join(player,room)
    count += 1


def create_several_rooms (n):
  for i in range (n):
    max_p = randint(5,10)
    room_name = "Pytherin" + str(i)
    #TODO max players
    create_room(owner,room_name)

#TODO test if the match still appearing even if it started
#hint: that should not happen
def test_main ():
  #This prints the room created by test_setup
  print(get_rooms())
  N_ROOMS = 5
  create_several_rooms(N_ROOMS)
  rooms = get_rooms()
  print("Rooms: " + rooms.__str__())
  real_rooms = rooms.get("room_list")
  room_names = []
  for room in real_rooms:
    room_names.append(room.get("name"))
  
  for i in range (0,N_ROOMS):
    n_players = randint(1,4)
    join_several_players(room_names[i],n_players)

  print("Rooms with people " + get_rooms().__str__())

  start_game(owner,room_names[0])
  print("\n\nStarted first room: " + get_rooms().__str__())

#main()
