from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from api.models.base import DB_User
from main import app

client = TestClient(app)


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

client.post(
    "/room/new",
    headers=owner,
    json={"name": "pytherin", "max_players": "5"}
)

join(owner, "pytherin")
join(p1, "pytherin")
join(p2, "pytherin")
join(p3, "pytherin")
join(p4, "pytherin")

response_get_pregame = client.get(
    "/pytherin/game_state",
    headers=p1
)
assert response_get_pregame.status_code == 200
print(response_get_pregame.json())

response_start = client.put(
    "/pytherin/start",
    headers=owner
)

response_get_ingame = client.get(
    "/pytherin/game_state",
    headers=p1
)

print(response_get_ingame.json())

assert response_start.status_code == 201

players = [owner, p1, p2, p3, p4]

director_email = "player1@email.com"
minister_email = None

for player in range(0, 5):
    response = client.put(
        "pytherin/director",
        json={"director_email": director_email},
        headers=players[player]
    )
    if response.status_code == 201:
        print("Minister: p" + str(player))
        print("Director: " + "p1")
        break

response_get_ingame2 = client.get(
    "/pytherin/game_state",
    headers=p1
)
print("\n")
print(response_get_ingame2.json())
print("\n")
""" 
TESTED: 
* Vote twice
* invalid vote
* Not in voting phase
"""

vote1 = client.put(
    "/pytherin/vote",
    headers=p1,
    json={
        'vote': "Lumos"
    })

vote2 = client.put(
    "/pytherin/vote",
    headers=p2,
    json={
        "vote": "Lumos"
    })
vote3 = client.put(
    "/pytherin/vote",
    headers=p3,
    json={
        "vote": "Nox"
    })
vote4 = client.put(
    "/pytherin/vote",
    headers=p4,
    json={
        "vote": "Nox"
    })
vote5 = client.put(
    "/pytherin/vote",
    headers=owner,
    json={
        "vote": "Lumos"
    })


assert vote1.status_code == 200
assert vote2.status_code == 200
assert vote3.status_code == 200
assert vote4.status_code == 200
assert vote5.status_code == 200

response_get_ingame = client.get(
    "/pytherin/game_state",
    headers=p2
)

for player in range(0, 5):
    response = client.get(
        "pytherin/cards",
        headers=players[player]
    )
    print(response.json())


for player in range(0, 5):
    response = client.put(
        "pytherin/discard",
        json={"card_index": 0},
        headers=players[player]
    )
    print(response.json())


for player in range(0, 5):
    response = client.get(
        "pytherin/cards",
        headers=players[player]
    )
    print(response.json())


for player in range(0, 5):
    response = client.put(
        "pytherin/discard",
        json={"card_index": 0},
        headers=players[player]
    )
    print(response.json())

response_get_postr1 = client.get(
    "/pytherin/game_state",
    headers=p2
)

print(response_get_postr1.json())
