from fastapi import APIRouter, HTTPException, status, Depends, Path
from api.models.room_models import RoomCreationRequest, DiscardRequest, ProposeDirectorRequest, VoteRequest
from api.handlers.authentication import *
from api.handlers.game_checks import *
from api.utils.room_utils import check_email_status, votes_to_json

from classes.room import Room, RoomStatus
from classes.room_hub import RoomHub
from classes.role_enum import Role
from classes.game_status_enum import GamePhase
from classes.game import Vote

router = APIRouter()

hub = RoomHub()


@router.post("/room/new", status_code=status.HTTP_201_CREATED)
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
        hub.add_room(new_room)
        return {"message": "Room created successfully"}


@router.get("/room/join/{room_name}", status_code=status.HTTP_200_OK)
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
        raise HTTPException(
            status_code=409, detail="You are already in this room")
    elif not room.is_open():
        raise HTTPException(status_code=403, detail="Room is full or in-game")
    else:
        await room.user_join(email)
        return {"message": f"Joined {room_name}"}


@router.get("/{room_name}/game_state", tags=["Game"], status_code=status.HTTP_200_OK)
async def get_game_state(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
            description="The room wich you want to get the game state of",
        ),
        email: str = Depends(valid_credentials)):

    room = hub.get_room_by_name(room_name)

    if not email in room.get_user_list():
        raise HTTPException(status_code=403, detail="You're not in this room")
    elif room.status == RoomStatus.PREGAME:
        return {"users": room.users, "owner": room.owner}
    elif room.status == RoomStatus.IN_GAME:
        game = room.get_game()

        my_role = game.get_player_role(email)
        if (my_role == Role.DEATH_EATER or my_role == Role.VOLDEMORT):
            de_list = game.get_de_list()
            voldemort = game.get_voldemort()
            # In next sprints, we need to check who is voldemort
            # and then show them the de_list
        else:
            de_list = []
            voldemort = ""

        json_r = {
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
    elif room.status == RoomStatus.FINISHED:
        # show results TO DO
        game = room.get_game()
        winner = game.get_phase()
        return {"message": f"Game has finished, {winner.name}"}


@router.put("/{room_name}/start", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def start_game(
        room_name: str = Path(
            ...,
            min_length=6,
            max_length=20,
        ),
        email: str = Depends(valid_credentials)):

    room = hub.get_room_by_name(room_name)

    if (room.owner != email):
        raise HTTPException(
            status_code=403, detail="You're not the owner of the room")
    elif (len(room.get_user_list()) < 5):
        raise HTTPException(
            status_code=409, detail="Not enough players")
    else:
        room.start_game()
        return {"message": "Succesfully started"}


@router.put("/{room_name}/director", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def propose_director(body: ProposeDirectorRequest,
                           room_name: str = Path(
                               ...,
                               min_length=6,
                               max_length=20,
                           ),
                           email: str = Depends(valid_credentials)):

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
            game.set_director(body.director_email)
            game.set_phase(GamePhase.VOTE_DIRECTOR)
            return {"message": "Director proposed successfully"}

    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@router.put("/{room_name}/vote", tags=["Game"], status_code=status.HTTP_200_OK)
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
    Throws 409 if the game is not in "voting phase"
    Throws 400 if the vote is not Lumos or Nox
    """

    room = check_game_preconditions(email, room_name, hub)
    game = room.get_game()

    if game.phase == GamePhase.VOTE_DIRECTOR:

        if vote_req.vote not in [Vote.LUMOS.value, Vote.NOX.value]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Invalid vote")
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
        room.update_status()

    return {"message": "Succesfully voted!"}


@router.get("/{room_name}/cards", tags=["Game"], status_code=status.HTTP_200_OK)
async def get_cards(
    room_name: str = Path(
        ...,
        min_length=6,
        max_length=20,
    ),
        email: str = Depends(valid_credentials)):

    room = check_game_preconditions(email, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    director = game.get_director_user()

    if ((phase == GamePhase.MINISTER_DISCARD and minister == email) or
            (phase == GamePhase.DIRECTOR_DISCARD and director == email)):
        return {"cards": game.get_cards()}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@router.put("/{room_name}/discard", tags=["Game"], status_code=status.HTTP_201_CREATED)
async def discard(body: DiscardRequest,
                  room_name: str = Path(
                      ...,
                      min_length=6,
                      max_length=20,
                  ),
                  email: str = Depends(valid_credentials)):

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
        room.update_status()
        return {"message": "Successfully discarded"}

    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)
