from fastapi import *
from api.routers.room_endpoints import hub

router = APIRouter()


@router.get("/rooms",status_code=status.HTTP_200_OK,tags=["Hub"])
async def get_rooms ():
  return {"message" : hub.all_rooms()}