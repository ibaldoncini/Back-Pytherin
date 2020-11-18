from  classes.game import Game
from api.routers.room_endpoints import chaos
from test_setup import p,create, start_game
from fastapi.testclient import TestClient
from test_main import test_app
from api.routers.hub_endpoints import get_rooms

client = TestClient(test_app)

owner = p[0]
p1 = p[1]
p2 = p[2]
p3 = p[3]
p4 = p[4]

#game = create(owner,"pytheroska")

""" 
def test_display ():
  response = client.get(
    "rooms/",
    headers=owner
  )
  print(response.json())
  assert response.status_code == 200
 """

response_start = start_game(owner,"test-game")

def test_wrong_phase ():
  response = client.put(
    "test-game/chaos",
    headers=owner
  )
  assert response.status_code == 405

""" 
def test_increase_chaos ():
  propose = client.post(
    "test-game/director",
    header=owner,
    json={}
  )
"""
