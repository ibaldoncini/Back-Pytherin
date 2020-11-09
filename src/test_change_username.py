# login_change_username.py
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from api.models.base import DB_User
from main import app


client = TestClient(app)


def register_and_login(email: str):
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

    return {"accept": "application/json", "Authorization": head}


p0 = register_and_login("lad0@noreply.com")
p1 = register_and_login("lad1@noreply.com")
p2 = register_and_login("lad2@noreply.com")


def test_change_username():  # happy path
    response = client.put(
        "/users/change_username",
        headers=p0,
        json={"username": "Malfoy"}
    )
    assert response.status_code == 200


def test_see_changes():
    response = client.get(
        "/users/me",
        headers=p0,
    )
    assert response.status_code == 200
    rta: dict = response.json()
    new_username: str = rta["username"]
    assert new_username == "Malfoy"


def test_invalid_new_uname1():
    response = client.put(
        "/users/change_username",
        headers=p2,
        json={"username": "as"}
    )
    assert response.status_code == 422


def test_invalid_new_uname2():
    response = client.put(
        "/users/change_username",
        headers=p2,
        json={"username": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}
    )
    assert response.status_code == 422
