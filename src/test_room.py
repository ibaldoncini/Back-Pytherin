# TODO - Room creation tests!

# When all conditions are met, is the room succesfully created?
# What happens if thers no email verificated?
# What about when the name is already in use?
# Or when the max player number is outside [5,10]?
# What if no user exists with that email?
# Or if a required parameter is missing?


"""
Always erase database before running this test
"""
from fastapi.testclient import TestClient
from main import app
from pony.orm import db_session, select, commit
from api.models.base import db, DB_User

client = TestClient(app)


client.post(
    "/users/register",
    json={
        "username": "jhonny_test",
        "email": "test@test.com",
        "password": "testtest",
        "icon": "stringstring",
        "emailConfirmed": "true",
        "logged": "true"
    }
)


def test_create_room():
    response = client.post(
        "/room/new",
        json={"name": "foobar", "max_players": "5",
              "email": "test@test.com"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Room created succesfully"}


def test_create_room_in_use_name():
    response = client.post(
        "/room/new",
        json={"name": "foobar", "max_players": "6",
              "email": "test@test.com"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Room name already in use"}


def test_create_room_4_players():
    response = client.post(
        "/room/new",
        json={"name": "foobar", "max_players": "4",
              "email": "test@test.com"}
    )
    assert response.status_code == 422


def test_create_room_11_players():
    response = client.post(
        "/room/new",
        json={"name": "foobar", "max_players": "11",
              "email": "test@test.com"}
    )
    assert response.status_code == 422


def test_create_room_missing_parameter():
    response = client.post(
        "/room/new",
        json={"max_players": "11",
              "email": "test@test.com"}
    )
    assert response.status_code == 422


def test_create_room_email_not_confirmed():
    with db_session:
        try:
            user = DB_User.get(email="test@test.com")
            user.set(emailConfirmed=False)
            commit()
        except:
            return None

    response = client.post(
        "/room/new",
        json={"name": "foobarfoobar", "max_players": "5",
              "email": "test@test.com"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "E-mail not confirmed"}

# def test_create_room_not_logged():
# def test_create_room_name length
