"""
Series Schemas

시리즈 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field

from .common import PaginatedResponse


class SeriesResponse(BaseModel):
    """시리즈 응답"""

    id: int
    catalog_id: str = Field(alias="catalogId")
    title: str
    year: int
    season_num: int | None = Field(None, alias="seasonNum")
    description: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    episode_count: int = Field(0, alias="episodeCount")

    class Config:
        from_attributes = True
        populate_by_name = True


class ContentSummary(BaseModel):
    """콘텐츠 요약 (시리즈 상세용)"""

    id: int
    episode_num: int | None = Field(None, alias="episodeNum")
    title: str
    duration_sec: int = Field(alias="durationSec")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    view_count: int = Field(alias="viewCount")
    hands_count: int = Field(alias="handsCount")

    class Config:
        from_attributes = True
        populate_by_name = True


class SeriesDetailResponse(BaseModel):
    """시리즈 상세 응답"""

    id: int
    catalog_id: str = Field(alias="catalogId")
    title: str
    year: int
    season_num: int | None = Field(None, alias="seasonNum")
    description: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    episode_count: int = Field(alias="episodeCount")
    contents: PaginatedResponse[ContentSummary]

    class Config:
        from_attributes = True
        populate_by_name = True
