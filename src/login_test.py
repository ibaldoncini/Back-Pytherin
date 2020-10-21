# login_test.py
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
"""
Execute test with command: pytest -v 
Delete the database before executing the test
"""


def test_load_user1():
    response = client.post(
        "/users/register",
        json={
            "user": {'username': 'test1',
                     'email': 'test1@mail.com',
                     'icon': 'string.png',
                     'emailConfirmed': True,
                     'logged': False
                     },
            "password": "Heladera63"
        }
    )
    assert response.status_code == 201
    assert response.json() == {"User registered:": "test1"}


def test_load_user2():
    response = client.post(
        "/users/register",
        json={
            "user": {'username': 'test2',
                     'email': 'test2@mail.com',
                     'icon': 'string.png',
                     'emailConfirmed': True,
                     'logged': False
                     },
            "password": "Heladera63"
        }
    )
    assert response.status_code == 201
    assert response.json() == {"User registered:": "test2"}


def test_load_user3():
    response = client.post(
        "/users/register",
        json={
            "user": {'username': 'test3',
                     'email': 'test3@mail.com',
                     'icon': 'string.png',
                     'emailConfirmed': True,
                     'logged': False
                     },
            "password": "Heladera63"
        }
    )
    assert response.status_code == 201
    assert response.json() == {"User registered:": "test3"}


def test_login_user_valid():
    response = client.post(
        "/users",
        data={
            "grant_type": '',
            "username": 'test1@mail.com',
            "password": 'Heladera63',
            "scope": '',
            "client_id": '',
            "client_secret": ''}
    )
    assert response.status_code == 200
    print(response.json())


def test_login_user_wrong_mail():
    response = client.post(
        "/users",
        data={
            "grant_type": '',
            "username": 'test2@gmail.com',
            "password": 'Heladera63',
            "scope": '',
            "client_id": '',
            "client_secret": ''}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect mail address"}


def test_login_user_wrong_pass():
    response = client.post(
        "/users",
        data={
            "grant_type": '',
            "username": 'test3@mail.com',
            "password": 'heladera63',
            "scope": '',
            "client_id": '',
            "client_secret": ''}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}


"""
-> To pass a path or query parameter, add it to the URL itself.
-> To pass a JSON body, pass a Python object (e.g. a dict) to the parameter json.
-> If you need to send Form Data instead of JSON, use the data parameter instead.
-> To pass headers, use a dict in the headers parameter.
-> For cookies, a dict in the cookies parameter.
"""
