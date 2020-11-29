import requests
from test_setup import p as players
from test_setup import unames
from classes.game_status_enum import GamePhase
from time import sleep
from random import randint, choice
import sys


messages: list = [
    "You most realize, you are doomed",
    "A surprise to be sure, but a welcome one",
    "This is where the fun begins",
    "DO IT",
    "There's Always A Bigger Fish",
    "I Don't Like Sand. It's Coarse And Rough And Irritating And It Gets Everywhere.",
    "Join me, and together we can rule the galaxy",
    "Did You Ever Hear The Tragedy Of Darth Plagueis The Wise?"
]

room_name = sys.argv[1]
index_in = sys.argv[2]
nof_players = int(sys.argv[3])
print(f"Room Name: {room_name} ")
print(f"Player index: {index_in}")
print(f"Number of player: {nof_players}")


index = int(index_in)
header = players[index]
nick = unames[index]

url = "http://127.0.0.1:8000"


join = requests.get(f"{url}/room/join/{room_name}", headers=header)
chat = requests.put(f"{url}/{room_name}/chat", json={"msg": "Hello There!"},
                    headers=header)

game_not_begun = True
while game_not_begun:
    sleep(3)
    r = requests.get(f"{url}/{room_name}/game_state", headers=header)
    state = r.json()
    if (state['room_status'] == "In game"):
        prob = randint(1, 4)
        sleep(prob)
        chat = requests.put(f"{url}/{room_name}/chat",
                            json={"msg": choice(messages)},
                            headers=header)
        game_not_begun = False
        break

while True:

    sleep(3)
    r = requests.get(f"{url}/{room_name}/game_state", headers=header)
    state = r.json()
    phase = state["phase"]
    minister = state["minister"]
    director = state["director"]
    my_role = state["my_role"]
    de_score = state["de_procs"]

    prob = randint(1, 4)
    if prob == 1:
        vote = 'Nox'
    else:
        vote = 'Lumos'

    print(f"\nMy name is: {nick}, minister : {minister}, phase: {phase}")

    if (str(phase) == str(GamePhase.PROPOSE_DIRECTOR.value) and nick == minister):
        requests.put(f"{url}/{room_name}/director",
                     json={"director_uname": unames[randint(0, nof_players)]},
                     headers=header)

    elif (str(phase) == str(GamePhase.VOTE_DIRECTOR.value)):
        requests.put(f"{url}/{room_name}/vote",
                     json={"vote": vote},
                     headers=header)

    elif (str(phase) == str(GamePhase.MINISTER_DISCARD.value) and nick == minister):
        requests.put(f"{url}/{room_name}/discard",
                     json={"card_index": "1"},
                     headers=header)

    elif (str(phase) == str(GamePhase.DIRECTOR_DISCARD.value) and nick == director):
        if de_score == 5:
            requests.put(f"{url}/{room_name}/discard",
                         json={"card_index": "3"},
                         headers=header)
        else:
            requests.put(f"{url}/{room_name}/discard",
                         json={"card_index": "1"},
                         headers=header)

    elif (str(phase) == str(GamePhase.REJECTED_EXPELLIARMUS.value) and nick == director):
        requests.put(f"{url}/{room_name}/discard",
                     json={"card_index": "1"},
                     headers=header)

    elif (str(phase) == str(GamePhase.CAST_CRUCIO.value) and nick == minister):
        requests.put(f"{url}/{room_name}/cast/crucio",
                     json={"target_uname": unames[randint(0, nof_players)]},
                     headers=header)
        requests.put(f"{url}/{room_name}/cast/confirm-crucio",
                     headers=header)

    elif (str(phase) == str(GamePhase.CAST_DIVINATION.value) and nick == minister):
        requests.get(f"{url}/{room_name}/cast/divination",
                     headers=header)
        requests.put(f"{url}/{room_name}/cast/confirm_divination",
                     headers=header)

    elif (str(phase) == str(GamePhase.CAST_IMPERIUS.value) and nick == minister):
        requests.put(f"{url}/{room_name}/cast/imperius",
                     json={"target_uname": unames[randint(0, nof_players)]},
                     headers=header)

    elif (str(phase) == str(GamePhase.CAST_AVADA_KEDAVRA.value) and nick == minister):
        victim = unames[randint(0, nof_players)]
        requests.put(f"{url}/{room_name}/cast/avada-kedavra",
                     json={"target_uname": victim},
                     headers=header)
        requests.put(f"{url}/{room_name}/chat",
                     json={"msg": f"It's over {victim}, i have the high ground"},
                     headers=header)

    elif (str(phase) == str(GamePhase.CONFIRM_EXPELLIARMUS.value) and nick == minister):
        print("Something")
        requests.put(f"{url}/{room_name}/expelliarmus",
                     json={"vote": vote},
                     headers=header)

    elif (str(phase) == str(GamePhase.DE_WON.value) or str(phase) == str(GamePhase.FO_WON.value)):
        print("Game has ended")
        break

    else:
        sleep(3)
        pass
