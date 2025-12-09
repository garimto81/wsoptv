"""
Hand Schemas

핸드 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field


class HandResponse(BaseModel):
    """핸드 응답"""

    id: int
    content_id: int = Field(alias="contentId")
    hand_number: int | None = Field(None, alias="handNumber")
    start_sec: int = Field(alias="startSec")
    end_sec: int = Field(alias="endSec")

    winner: str | None = None
    pot_size_bb: float | None = Field(None, alias="potSizeBb")
    is_all_in: bool = Field(alias="isAllIn")
    is_showdown: bool = Field(alias="isShowdown")

    board: str | None = None
    grade: str
    tags: list[str] = []
    highlight_score: int = Field(alias="highlightScore")

    players: list[str]

    class Config:
        from_attributes = True
        populate_by_name = True


class HandListResponse(BaseModel):
    """핸드 목록 응답"""

    items: list[HandResponse]
    total: int
