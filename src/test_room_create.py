
from fastapi.testclient import TestClient
from test_main import test_app
from pony.orm import db_session, commit
from api.models.base import db

client = TestClient(test_app)


client.post(
    "/users/register",
    json={
        "username": "jhonny_test",
        "email": "test@test.com",
        "password": "Heladera64",
        "icon": "string"
    }
)

response_login = client.post(
    "/users",
    data={
        "grant_type": '',
        "username": 'test@test.com',
        "password": 'Heladera64',
        "scope": '',
        "client_id": '',
        "client_secret": ''}
)
assert response_login.status_code == 200
rta: dict = response_login.json()
token: str = rta['access_token']
token_type: str = 'Bearer '
head: str = token_type + token


# test no login
def test_no_login():
    response = client.post(
        "/room/new",
        json={"name": "foobar", "max_players": "5"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"}


# test login no mail
def test_unconfirmed_mail():
    response = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foobar", "max_players": "5"}
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "E-mail not confirmed"}


# test login and mail bad arguments
def test_bad_json():
    with db_session:
        try:
            user = db.DB_User.get(email="test@test.com")
            user.set(email_confirmed=True)
            commit()
        except:
            return None

    response1 = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foobar"}
    )

    response2 = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foobar", "max_players": "4"}
    )

    response3 = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foo", "max_players": "5"}
    )

    assert response1.status_code == 422
    assert response2.status_code == 422
    assert response3.status_code == 422


# test login and mail good arguments (htest_appy path)
def test_htest_appy_path():
    response = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foobar", "max_players": "5"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "message": "Room created successfully"}


# test login and mail in use nam
def test_used_name():
    response = client.post(
        "/room/new",
        headers={"accept": "test_application/json",
                 "Authorization": head
                 },
        json={"name": "foobar", "max_players": "6"}
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Room name already in use"}
