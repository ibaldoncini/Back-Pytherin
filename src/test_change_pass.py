# login_change_password.py
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


p0 = register_and_login("person0@noreply.com")
p1 = register_and_login("person1@noreply.com")
p2 = register_and_login("person2@noreply.com")


def test_change_password():  # happy path
    response = client.put(
        "/users/change_password",
        headers=p0,
        json={"old_pwd": "Heladera65",
              "new_pwd": "Refrigerador65"}
    )
    assert response.status_code == 200


def test_relogin_with_new_pass():
    response = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "person0@noreply.com",
            "password": "Refrigerador65",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response.status_code == 200


def test_wrong_psw():
    response = client.put(
        "/users/change_password",
        headers=p1,
        json={"old_pwd": "ASDaSD77",
              "new_pwd": "Refrigerador65"}
    )
    assert response.status_code == 401


def test_invalid_new_psw1():
    response = client.put(
        "/users/change_password",
        headers=p2,
        json={"old_pwd": "Heladera65",
              "new_pwd": "heladera"}
    )
    assert response.status_code == 422


def test_invalid_new_psw2():
    response = client.put(
        "/users/change_password",
        headers=p2,
        json={"old_pwd": "Heladera65",
              "new_pwd": "Helado"}
    )
    assert response.status_code == 422


def test_invalid_new_psw3():
    response = client.put(
        "/users/change_password",
        headers=p2,
        json={"old_pwd": "Heladera65",
              "new_pwd": "7aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}
    )
    assert response.status_code == 422
