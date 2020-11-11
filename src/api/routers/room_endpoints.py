from fastapi import APIRouter, HTTPException, status, Depends, Path
from api.models.room_models import *
from api.handlers.authentication import *
from api.handlers.game_checks import *
from api.utils.room_utils import check_email_status, votes_to_json

from classes.room import Room, RoomStatus
from classes.room_hub import RoomHub
from classes.role_enum import Role
from classes.game_status_enum import GamePhase
from classes.game import Vote
from api.models.base import db, save_game_on_database, dump_room  # , Room

router = APIRouter()

hub = RoomHub()


@router.post("/room/new", tags=["Room"], status_code=status.HTTP_201_CREATED)
async def create_room(
    room_info: RoomCreationRequest, email: str = Depends(valid_credentials)
):
    """
    Endpoint for creating a new room.

    Possible respones:\n
            201 when succesfully created.
            401 when not logged in.
            403 when email not confirmed.
            409 when the room name is already in use.
            500 when there's an internal error in the database.
    """

    room_name = room_info.name
    max_players = room_info.max_players
    email_confirmed = await check_email_status(email)

    if not email_confirmed:
        raise HTTPException(status_code=403, detail="E-mail not confirmed")
    elif room_name in (hub.all_rooms()):
        raise HTTPException(status_code=409, detail="Room name already in use")
    else:
        new_room = Room(room_name, max_players, email)
        await save_game_on_database(new_room)
        hub.add_room(new_room)
        return {"message": "Room created successfully"}


@router.get("/room/join/{room_name}", tags=["Room"], status_code=status.HTTP_200_OK)
async def join_room(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
            description="The name of the room you want to join",
        ),
        email: str = Depends(valid_credentials)):
    """
    Endpoint to join a room, it takes the room name as a parameter in the URL,
    and the access_token in the request headers.

    Possible respones:\n
            200 when succesfully joined.
            401 when not logged in.
            403 when email not confirmed.
            404 when the room doesn't exist.
            409 when the user is already in the room.
            403 when the room is full or in-game.
    """

    room = hub.get_room_by_name(room_name)
    if not await check_email_status(email):
        raise HTTPException(status_code=403, detail="E-mail is not confirmed")
    elif not room:
        raise HTTPException(status_code=404, detail="Room not found")
    elif email in room.get_user_list():
        return {"message": f"Joined {room_name}"}
    elif not room.is_open():
        raise HTTPException(status_code=403, detail="Room is full or in-game")
    else:
        await save_game_on_database(room)
        await room.user_join(email)
        return {"message": f"Joined {room_name}"}


@router.get("/room/leave/{room_name}", tags=["Room"], status_code=status.HTTP_200_OK)
async def leave_room(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
            description="The name of the room you want to leave",
        ),
        email: str = Depends(valid_credentials)):
    """
    Endpoint to leave a room, it takes the room name as a parameter in the URL,
    and the access_token in the request headers.

    Possible respones:\n
            200 when succesfully left.
            401 when not logged in.
            403 when email not confirmed.
            404 when the room doesn't exist.
            409 when the user is not in the room.
            403 when the room is full or in-game.
    """

    room = hub.get_room_by_name(room_name)
    if not await check_email_status(email):
        raise HTTPException(status_code=403, detail="E-mail is not confirmed")
    elif not room:
        raise HTTPException(status_code=404, detail="Room not found")
    elif email not in room.get_user_list():
        raise HTTPException(status_code=409, detail="You're not in this room")
    elif room.status == RoomStatus.IN_GAME:
        raise HTTPException(status_code=403, detail="Room is in-game")
    else:
        await room.user_leave(email)
        return {"message": f"Left {room_name}"}


@router.get("/{room_name}/game_state", tags=["Game"], status_code=status.HTTP_200_OK)
async def get_game_state(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
            description="The room wich you want to get the game state of",
        ),
        email: str = Depends(valid_credentials)):

    """
    Endpoint for getting the state of the game at every moment

    Will return the list of users in the room, and the room owner if the game
    hasn't started yet.

    A json containing the following game info if is has already started:
            "my_role": the role of the player who requested the game sate,
            "death_eaters": if my role is DE, this contains a list of the other deatheaters,
            "voldemort": if you are DE, who is voldemort,
            "minister": this turn's minister,
            "director": the proposed director,
            "last_minister": the previous minister,
            "last_director": the previous director,
            "de_procs": DeathEater proclamations,
            "fo_procs": FenixOrder proclamations,
            "phase": the phase the game is in propose director, vote,
                     minister discard ,director discard, (1,2,3,4) respectively,
            "player_list": the players in the game,
            "votes": the player votes for this turn.

    Or it will return the winner if the game is over
    """
    room = hub.get_room_by_name(room_name)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    elif not email in room.get_user_list():
        raise HTTPException(status_code=403, detail="You're not in this room")
    elif room.status == RoomStatus.PREGAME:
        return {"room_status": room.status, "users": room.users, "owner": room.owner}
    else:
        room.update_status()
        game = room.get_game()
        my_role = game.get_player_role(email)

        if (my_role == Role.DEATH_EATER or my_role == Role.VOLDEMORT or room.status == RoomStatus.FINISHED):
            de_list = game.get_de_list()
            voldemort = game.get_voldemort()
            # In next sprints, we need to check who is voldemort
            # and then show them the de_list
        else:
            de_list = []
            voldemort = ""

        json_r = {
            "room_status": room.status,
            "my_role": my_role,
            "death_eaters": de_list,
            "voldemort": voldemort,
            "minister": game.get_minister_user(),
            "director": game.get_director_user(),
            "last_minister": game.get_last_minister_user(),
            "last_director": game.get_last_director_user(),
            "de_procs": game.get_de_procs(),
            "fo_procs": game.get_fo_procs(),
            "phase": game.get_phase(),
            "player_list": game.get_current_players(),
            "votes": votes_to_json(game.get_votes())
        }
        return json_r


@router.put("/{room_name}/start", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def start_game(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
        ),
        email: str = Depends(valid_credentials)):
    """
    Endpoint for starting the game, should only be used by the room owner.

    Will only work if there are 5 players or more.
    """
    room = hub.get_room_by_name(room_name)

    if (room.owner != email):
        raise HTTPException(
            status_code=403, detail="You're not the owner of the room")
    elif (len(room.get_user_list()) < 5):
        raise HTTPException(
            status_code=409, detail="Not enough players")
    else:
        await save_game_on_database(room)
        room.start_game()
        return {"message": "Succesfully started"}


@router.get("/{room_name}/dump", tags=["Game"])
async def dump(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
        ),
        email: str = Depends(valid_credentials)):
    room = hub.get_room_by_name(room_name)
    return dump_room(room)


@router.put("/{room_name}/director", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def propose_director(body: ProposeDirectorRequest,
                           room_name: str = Path(
                               ...,
                               min_length=6,
                               max_length=20,
                           ),
                           email: str = Depends(valid_credentials)):

    """
    Endpoint used by the minister to propose the director
    """
    room = check_game_preconditions(email, room_name, hub)
    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.PROPOSE_DIRECTOR and minister == email):
        if body.director_email not in game.get_current_players():
            raise HTTPException(
                status_code=404, detail="Player not found")
        elif (body.director_email == game.get_last_director_user()
              or minister == body.director_email):
            raise HTTPException(
                status_code=403, detail="That player cannot be the director this round")
        else:

            await save_game_on_database(room)

            game.set_director(body.director_email)
            game.set_phase(GamePhase.VOTE_DIRECTOR)
            return {"message": "Director proposed successfully"}

    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/vote", tags=["Game"], status_code=status.HTTP_200_OK)
async def vote(
        vote_req: VoteRequest,
        email: str = Depends(valid_credentials),
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
        )):
    """
    This endpoint registers a vote and who`s voting.
    Throws 409 if the game if you already voted
    Throws 405 if the game is not in phase of voting
    Throws 400 if the vote is not Lumos or Nox
    """

    room = check_game_preconditions(email, room_name, hub)
    game = room.get_game()

    if game.phase == GamePhase.VOTE_DIRECTOR:

        if vote_req.vote not in [Vote.LUMOS.value, Vote.NOX.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vote")
        elif email in game.get_votes().keys():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="You already voted")
        else:
            game.register_vote(vote_req.vote, email)

    else:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Game is not in voting phase")

    if len(game.get_current_players()) == len(game.votes):
        game.compute_votes()

    return {"message": "Succesfully voted!"}


@ router.get("/{room_name}/cards", tags=["Game"], status_code=status.HTTP_200_OK)
async def get_cards(
    room_name: str = Path(
        ...,
        min_length=6,
        max_length=20,
    ),
        email: str = Depends(valid_credentials)):

    """
    Endpoint for getting the cards, used both by minister and director, but at their respective times.
    Will return a list similar to this:

    ['Order of the Fenix proclamation',
        'Order of the Fenix proclamation', 'Death Eater proclamation']
    """
    room = check_game_preconditions(email, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    director = game.get_director_user()

    if ((phase == GamePhase.MINISTER_DISCARD and minister == email) or
            (phase == GamePhase.DIRECTOR_DISCARD and director == email)):
        #
        return {"cards": game.get_cards()}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/discard", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def discard(body: DiscardRequest,
                  room_name: str = Path(
                      ...,
                      min_length=6,
                      max_length=20,
                  ),
                  email: str = Depends(valid_credentials)):

    """
    Endpoint used for discarding a card, both by minister and director.

    Expects a body containing 1 field ("card_index") that represents the index of the card
    you want to discard (as returned by the /cards endpoint)
    """

    room = check_game_preconditions(email, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    if (phase == GamePhase.MINISTER_DISCARD and game.get_minister_user() == email):
        if (body.card_index not in [0, 1, 2]):
            raise HTTPException(
                detail="Index out of bounds", status_code=400)

        game.discard(body.card_index)
        game.set_phase(GamePhase.DIRECTOR_DISCARD)
        return {"message": "Successfully discarded"}

    elif (phase == GamePhase.DIRECTOR_DISCARD and game.get_director_user() == email):
        if (body.card_index not in [0, 1]):
            raise HTTPException(
                detail="Index out of bounds", status_code=400)

        game.discard(body.card_index)
        game.proc_leftover_card()
        return {"message": "Successfully discarded"}

    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.get("/{room_name}/cast/divination", tags=["Game"], status_code=status.HTTP_200_OK)
async def cast_divination(room_name: str = Path(..., min_length=6, max_length=20),
                          email: str = Depends(valid_credentials)):

    room = check_game_preconditions(email, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.CAST_DIVINATION and email == minister):
        return {"cards": game.divination()}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/cast/avada-kedavra", tags=["Game"], status_code=status.HTTP_200_OK)
async def cast_avada_kedavra(body: TargetedSpellRequest,
                             room_name: str = Path(...,
                                                   min_length=6, max_length=20),
                             email: str = Depends(valid_credentials)):

    room = check_game_preconditions(email, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.CAST_AVADA_KEDAVRA and email == minister):
        if body.target_email not in game.get_current_players():
            raise HTTPException(detail="Player not found", status_code=404)
        elif body.target_email not in game.get_alive_players():
            raise HTTPException(
                detail="Player is already dead", status_code=409)
        else:
            game.avada_kedavra(body.target_email)
            return {"message": "Successfully casted Avada Kedavra"}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)
