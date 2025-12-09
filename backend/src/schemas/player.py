"""
Player Schemas

플레이어 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field


class PlayerResponse(BaseModel):
    """플레이어 응답"""

    id: int
    name: str
    display_name: str = Field(alias="displayName")
    country: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")
    total_hands: int = Field(alias="totalHands")
    total_wins: int = Field(alias="totalWins")
    win_rate: float = Field(alias="winRate")

    class Config:
        from_attributes = True
        populate_by_name = True


class PlayerListResponse(BaseModel):
    """플레이어 목록 응답"""

    items: list[PlayerResponse]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True
