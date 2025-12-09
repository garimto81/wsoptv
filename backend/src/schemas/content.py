"""
Content Schemas

콘텐츠 관련 Pydantic 스키마
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .common import PaginatedResponse


class ContentResponse(BaseModel):
    """콘텐츠 응답"""

    id: int
    series_id: int = Field(alias="seriesId")
    episode_num: int | None = Field(None, alias="episodeNum")
    title: str
    description: str | None = None
    duration_sec: int = Field(alias="durationSec")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    view_count: int = Field(alias="viewCount")
    hands_count: int = Field(0, alias="handsCount")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class SeriesInfo(BaseModel):
    """시리즈 정보 (콘텐츠 상세용)"""

    id: int
    catalog_id: str = Field(alias="catalogId")
    title: str
    year: int

    class Config:
        from_attributes = True
        populate_by_name = True


class HandSummary(BaseModel):
    """핸드 요약 (콘텐츠 상세용)"""

    id: int
    hand_number: int | None = Field(None, alias="handNumber")
    start_sec: int = Field(alias="startSec")
    end_sec: int = Field(alias="endSec")
    grade: str
    players: list[str]
    is_all_in: bool = Field(alias="isAllIn")

    class Config:
        from_attributes = True
        populate_by_name = True


class ContentDetailResponse(BaseModel):
    """콘텐츠 상세 응답"""

    id: int
    title: str
    description: str | None = None
    duration_sec: int = Field(alias="durationSec")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    view_count: int = Field(alias="viewCount")
    episode_num: int | None = Field(None, alias="episodeNum")
    series: SeriesInfo
    stream_url: str | None = Field(None, alias="streamUrl")
    hands: list[HandSummary]
    hands_count: int = Field(alias="handsCount")

    class Config:
        from_attributes = True
        populate_by_name = True


class ContentListResponse(BaseModel):
    """콘텐츠 목록 응답"""

    items: list[ContentResponse]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True
