
from api.models.room_models import TargetedSpellRequest
from api.handlers.authentication import get_username_from_token
from api.handlers.game_checks import check_game_preconditions
from api.routers.room_endpoints import hub

from classes.game_status_enum import GamePhase

from fastapi import APIRouter, HTTPException, status, Depends, Path

router = APIRouter()


@ router.get("/{room_name}/cast/divination", tags=["Spells"], status_code=status.HTTP_200_OK)
async def cast_divination(room_name: str = Path(..., min_length=6, max_length=20),
                          username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.CAST_DIVINATION and username == minister):
        return {"cards": game.divination()}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/cast/confirm_divination", tags=["Spells"], status_code=status.HTTP_200_OK)
async def confirm_divination(room_name: str = Path(..., min_length=6, max_length=20),
                             username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()

    if (phase == GamePhase.CAST_DIVINATION and username == minister):
        game.restart_turn()
        return {"message": "Divination confirmed, moving on"}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/cast/avada-kedavra", tags=["Spells"], status_code=status.HTTP_200_OK)
async def cast_avada_kedavra(body: TargetedSpellRequest,
                             room_name: str = Path(...,
                                                   min_length=6, max_length=20),
                             username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.CAST_AVADA_KEDAVRA and username == minister):
        if body.target_uname not in game.get_current_players():
            raise HTTPException(detail="Player not found", status_code=404)
        elif body.target_uname not in game.get_alive_players():
            raise HTTPException(
                detail="Player is already dead", status_code=409)
        else:
            game.avada_kedavra(body.target_uname)
            return {"message": "Successfully casted Avada Kedavra"}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.get("/{room_name}/cast/crucio", tags=["Spells"], status_code=status.HTTP_200_OK)
async def cast_crucio(body: TargetedSpellRequest,
                      room_name: str = Path(...,
                                            min_length=6, max_length=20),
                      username: str = Depends(get_username_from_token)):
    """ 
    Endpoint that casts the spell "crucio", revealing the loyalty of some
    player to the minister.
    THROWS:
    200 if OK
    400 if game is not in CAST_CRUCIO phase
    405 if who made the request is not the minister
    406 if the victim is the minister (minister voted himself)
    409 if the playet is dead or was already investigated 
    """
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    victim = body.target_uname
    if username == minister:
        if phase != GamePhase.CAST_CRUCIO:
            raise HTTPException(
                detail="Game is not in Cruciatus phase",status_code=400)
        elif victim not in game.get_alive_players():
            raise HTTPException(
                detail="Let him rest in peace!",status_code=409)
        elif victim == minister:
            raise HTTPException(
                detail="You can`t choose yourself",status_code=406)
        elif victim in game.get_investigated_players():
            raise HTTPException(
                detail="Player already investigated",status_code=409)
        else:
            return {"loyalty": game.crucio(victim)}
    else:
        raise HTTPException(
                detail="You`re not allowed to do this",status_code=405)



@ router.put("/{room_name}/cast/confirm-crucio", tags=["Spells"], status_code=status.HTTP_200_OK)
async def confirm_crucio(room_name: str = Path(..., min_length=6, max_length=20),
                         username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()

    if (phase == GamePhase.CAST_CRUCIO and username == minister):
        game.restart_turn()
        return {"message": "Divination confirmed, moving on"}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/cast/imperius", tags=["Spells"], status_code=status.HTTP_200_OK)
async def cast_imperius(body: TargetedSpellRequest,
                        room_name: str = Path(...,
                                              min_length=6, max_length=20),
                        username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()
    if (phase == GamePhase.CAST_IMPERIUS and username == minister):
        if body.target_uname not in game.get_current_players():
            raise HTTPException(detail="Player not found", status_code=404)
        elif body.target_uname == minister:
            raise HTTPException(
                detail="You cant choose yourself", status_code=409)
        else:
            game.imperius(casted_by=minister, target=body.target_uname)
            return {"message": "Successfully casted Imperius"}
    else:
        raise HTTPException(
            detail="You're not allowed to do this", status_code=405)


@ router.put("/{room_name}/cast/expelliarmus", tags=["Spells"], status_code=status.HTTP_200_OK)
async def cast_expelliarmus(room_name: str = Path(
                            ..., min_length=6, max_length=20),
                            username: str = Depends(get_username_from_token)):
    global hub
    room = check_game_preconditions(username, room_name, hub)

    game = room.get_game()
    phase = game.get_phase()
    minister = game.get_minister_user()

    return {"message": "Successfully casted Expelliarmus"}
