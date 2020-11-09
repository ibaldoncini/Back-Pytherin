# login_test.py
from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from api.models.base import DB_User
from main import app

client = TestClient(app)
"""
Execute test with command: pytest -v 
Delete the database before executing the test
"""


def load_user1():
    response = client.post(
        "/users/register",
        json={
            "username": "test1",
            "email": "test1@mail.com",
            "password": "Heladera63",
            "icon": "string",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "test1, a verification email has been sent to test1@mail.com"
    }


def load_user2():
    response = client.post(
        "/users/register",
        json={
            "username": "test2",
            "email": "test2@mail.com",
            "password": "Heladera63",
            "icon": "string",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "test2, a verification email has been sent to test2@mail.com"
    }


def load_user3():
    response = client.post(
        "/users/register",
        json={
            "username": "test3",
            "email": "test3@mail.com",
            "password": "Heladera63",
            "icon": "string",
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "test3, a verification email has been sent to test3@mail.com"
    }


load_user1()
load_user2()
load_user3()


def test_login_user_valid():
    response = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test1@mail.com",
            "password": "Heladera63",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response.status_code == 200


def test_login_user_wrong_mail():
    response = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test2@gmail.com",
            "password": "Heladera63",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect mail address"}


def test_login_user_wrong_pass():
    response = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test3@mail.com",
            "password": "heladera63",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}


def test_invalid_token_user():
    response = client.get(
        "/users/me",
        headers={"accept": "application/json",
                 "Authorization": "Bearer a.bad.token"},
    )
    assert response.status_code == 401


def test_login_and_token_user():
    with db_session:
        try:
            user = DB_User.get(email="test3@test3.com")
            user.set(email_confirmed=True)
            commit()
        except:
            return None

    response_login = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test3@mail.com",
            "password": "Heladera63",
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
    response_token = client.get(
        "/users/me", headers={"accept": "application/json", "Authorization": head}
    )
    assert response_token.json() == ""
    assert response_token.status_code == 200


def test_login_and_refresh_token():
    response_login = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test3@mail.com",
            "password": "Heladera63",
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
    response_token = client.put(
        "/users/refresh", headers={"accept": "application/json", "Authorization": head}
    )
    assert response_token.status_code == 201


def test_login_and_get():
    with db_session:
        try:
            user = DB_User.get(email="test1@test1.com")
            user.set(email_confirmed=True)
            commit()
        except:
            return None

    response_login = client.post(
        "/users",
        data={
            "grant_type": "",
            "username": "test1@mail.com",
            "password": "Heladera63",
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
    response_get = client.get(
        "/users/me", headers={"accept": "application/json", "Authorization": head}
    )
    assert response_get.status_code == 200


"""
-> To pass a path or query parameter, add it to the URL itself.
-> To pass a JSON body, pass a Python object (e.g. a dict) to the parameter json.
-> If you need to send Form Data instead of JSON, use the data parameter instead.
-> To pass headers, use a dict in the headers parameter.
-> For cookies, a dict in the cookies parameter.
"""
