# test_setup.py
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from api.models.base import db
from test_main import test_app


client = TestClient(test_app)


def register(email: str):
    client.post(
        "/users/register",
        json={
            "username": email.split('@')[0],
            "email": email,
            "password": "Heladera65",
            "icon": "string",
        })
    with db_session:
        try:
            user = db.DB_User.get(email=email)
            user.set(email_confirmed=True)
            commit()
        except Exception as e:
            print(e)
            pass
    pass


def login(email: str):
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

    return {"accept": "application/json", "Authorization": head}


def create(header, room_name: str):
    client.post(
        "/room/new",
        headers=header,
        json={"name": f"{room_name}", "max_players": "5"}
    )


def join(header, room_name: str):
    client.get(
        f"/room/join/{room_name}",
        headers=header,
    )


def start_game(owner, room_name: str):
    response = client.put(
        f"/{room_name}/start",
        headers=owner
    )
    return response


def vote(header: str, vote: str, room_name: str):
    response = client.put(
        f"/{room_name}/vote",
        headers=header,
        json={
            "vote": vote
        }
    )
    return response


p = []
unames = []
for i in range(0, 5):
    unames.append(f"player{i}")
    # print(f"player{i}@example.com")
    register(f"player{i}@example.com")
    p.append(login(f"player{i}@example.com"))

create(p[0], "pytherin")
join(p[0], "pytherin")
join(p[1], "pytherin")
join(p[2], "pytherin")
join(p[3], "pytherin")
join(p[4], "pytherin")
