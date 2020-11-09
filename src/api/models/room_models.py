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


class VoteRequest(BaseModel):
    """
    Body of the request used to vote
    """
    vote: str = Field(..., description="Vote = <lumos/nox>")


class DiscardRequest(BaseModel):
    """
    Body of the request used for discarding a card.
    Used by minister and director only.
    """
    card_index: int = Field(..., ge=0, le=2,
                            description="The index of the card to be discarded")


class ProposeDirectorRequest(BaseModel):
    """
    Body of the request used for proposing a director.
    Used by minister only.
    """
    director_email: str = Field(...,
                                description="The email of the user to be proposed as director")


class TargetedSpellRequest(BaseModel):
    """
    Body of the request used for spells that are casted onto another player
    """
    target_email: str = Field(...,
                              description="The email of the user to receive the spell")
