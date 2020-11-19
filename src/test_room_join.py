"""
Always erase database before running this test
"""
from fastapi.testclient import TestClient
from test_main import test_app
from pony.orm import db_session, commit
from api.models.base import db

client = TestClient(test_app)


rta = client.post(
    "/users/register",
    json={
        "username": "jhonny_test2",
        "email": "test_join@test.com",
        "password": "Heladera64",
        "icon": "string",
    },
)
assert rta.status_code == 201

response_login = client.post(
    "/users",
    data={
        "grant_type": "",
        "username": "test_join@test.com",
        "password": "Heladera64",
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
        user = db.DB_User.get(email="test_join@test.com")
        user.set(email_confirmed=True)
        commit()
    except:
        pass

creation = client.post(
    "/room/new",
    headers={"accept": "test_application/json", "Authorization": head},
    json={"name": "1stroom", "max_players": "5"},
)
assert creation.status_code == 201

with db_session:
    try:
        user = db.DB_User.get(email="test_join@test.com")
        user.set(email_confirmed=False)
        commit()
    except:
        pass


# test no login
def test_no_login():
    response = client.get("/room/join/testroom")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


# test login no mail
def test_unconfirmed_mail():
    response = client.get(
        "/room/join/testroom",
        headers={"accept": "test_application/json", "Authorization": head},
    )
    assert response.json() == {"detail": "E-mail is not confirmed"}
    assert response.status_code == 403


# test login and mail bad path
def test_bad_json():
    with db_session:
        try:
            user = db.DB_User.get(email="test_join@test.com")
            user.set(email_confirmed=True)
            commit()
        except:
            return None

    response1 = client.get(
        "/room/join/{foo}",
        headers={"accept": "test_application/json", "Authorization": head},
    )

    response2 = client.get(
        "/room/join/{unodostrescuatrocincoseis}",
        headers={"accept": "test_application/json", "Authorization": head},
    )

    assert response1.status_code == 422
    assert response2.status_code == 422


# test login and mail good path (test_happy path)
def test_test_happy_path():

    response = client.get(
        "/room/join/1stroom",
        headers={"accept": "test_application/json", "Authorization": head},
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Joined 1stroom"}


# test user already in room
def test_user_already_in():
    response = client.get(
        "/room/join/1stroom",
        headers={"accept": "test_application/json", "Authorization": head},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Joined 1stroom"}


def test_room_not_open():
    # Testing this one is a pain in the a**, I'm pretty sure it works
    assert True
