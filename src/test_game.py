from fastapi.testclient import TestClient
from pony.orm import db_session, commit
from api.models.base import db
from test_main import test_app
from test_setup import p, start_game, unames, vote

client = TestClient(test_app)


# def test_start_and_first_round():
response_get_pregame1 = client.get(
    "/pytherin/game_state",
    headers=p[0]
)
assert response_get_pregame1.status_code == 200

start_game(p[0], "pytherin")

we_know_who_voldemort_is = False
while not we_know_who_voldemort_is:
    j = 0
    response_get_pregame = client.get(
        "/pytherin/game_state",
        headers=p[j]
    )
    rta: dict = response_get_pregame.json()
    voldemort_uname = rta["voldemort"]
    if voldemort_uname != "":
        we_know_who_voldemort_is = True
    else:
        j += 1

round_count = 0
game_is_not_over = True
de_score = 0
fo_score = 0
divination_casted = False
avadas_avaliables = 2


while game_is_not_over:
    round_count += 1
    response_get_ingame = client.get(
        "/pytherin/game_state",
        headers=p[0]
    )
    assert response_get_ingame.status_code == 200

    rta: dict = response_get_ingame.json()
    print(f"\nStart of round {round_count}")
    print(rta)
    minister_uname: str = rta["minister"]
    minister_index = unames.index(minister_uname)
    director_index = (minister_index + 1) % 5
    director_uname: str = unames[director_index]
    alive_lads = rta["player_list"]

    respone_propose = client.put(
        "/pytherin/director",
        json={"director_email": director_uname},
        headers=p[minister_index]
    )
    assert respone_propose.status_code == 201

    for i in range(0, 5):
        if unames[i] in alive_lads:
            if (i % 2):
                response = vote(header=p[i], vote="Nox", room_name="pytherin")
            else:
                response = vote(
                    header=p[i], vote="Lumos", room_name="pytherin")
            assert response.status_code == 200
        else:
            response = vote(header=p[i], vote="Nox", room_name="pytherin")
            assert response.status_code == 403

    response_get_ingame2 = client.get(
        "/pytherin/game_state",
        headers=p[0]
    )
    assert response_get_ingame2.status_code == 200
    print("\nAfter the voting")
    print(response_get_ingame2.json())

    if de_score > 2 and voldemort_uname == director_uname:
        print("Death eaters won, voldi runs hogwarts")
        game_is_not_over = False
        break

    response_get_cards1 = client.get(
        "pytherin/cards",
        headers=p[minister_index]
    )
    assert response_get_cards1.status_code == 200

    response_discard1 = client.put(
        "pytherin/discard",
        json={"card_index": 0},
        headers=p[minister_index]
    )
    assert response_discard1.status_code == 201

    response_get_cards2 = client.get(
        "pytherin/cards",
        headers=p[director_index]
    )
    assert response_get_cards2.status_code == 200

    response_discard2 = client.put(
        "pytherin/discard",
        json={"card_index": 0},
        headers=p[director_index]
    )
    assert response_discard2.status_code == 201

    response_post_proclamation = client.get(
        "/pytherin/game_state",
        headers=p[0]
    )
    assert response_post_proclamation.status_code == 200
    scores_state: dict = response_post_proclamation.json()
    de_score = scores_state["de_procs"]
    fo_score = scores_state["fo_procs"]

    if de_score == 6:
        print("Death eaters won")
        game_is_not_over = False
        break
    elif fo_score == 5:
        print("Phoenix order won")
        break
    else:
        pass

    if de_score == 3:
        response_cast_divination = client.get(
            "/pytherin/cast/divination",
            headers=p[minister_index]
        )
        if not divination_casted:
            assert response_cast_divination.status_code == 200
            print("\n Next 3 cards:")
            print(response_cast_divination.json())
        else:
            assert response_cast_divination.status_code == 405

        response_confirm_divination = client.put(
            "/pytherin/cast/confirm_divination",
            headers=p[minister_index]
        )
        if not divination_casted:
            assert response_confirm_divination.status_code == 200
        else:
            assert response_confirm_divination.status_code == 405

        divination_casted = True

    if (de_score == 4 or de_score == 5) and avadas_avaliables >= 1:
        #victim_index = (minister_index - 1) % 5
        #victim_uname = unames[victim_index]
        if minister_index != 3 and avadas_avaliables > 1:
            victim_index = 3
            victim_uname = unames[victim_index]
        else:
            victim_index = 4
            victim_uname = unames[victim_index]

        response_cast_avada = client.put(
            "/pytherin/cast/avada-kedavra",
            headers=p[minister_index],
            json={"target_email": victim_uname}
        )
        assert response_cast_avada.status_code == 200
        print(response_cast_avada.json())
        avadas_avaliables -= 1
        if victim_uname == voldemort_uname:
            print("Voldemort died, F")
            game_is_not_over = False

    print("--------------------------------------------------")
