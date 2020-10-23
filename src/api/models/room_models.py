from pydantic import BaseModel, Field


class RoomCreationRequest(BaseModel):
    """
    Body of the request used to create a new room,
    Identifying owner by email isn't optimal(?)
    """
    name: str = Field(..., min_length=6, max_length=20,
                      description="The room's name")
    max_players: int = Field(
        ..., ge=5, le=10, description="Max allowed players in the room")
