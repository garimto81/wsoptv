"""
Search Schemas

검색 관련 Pydantic 스키마
"""

from typing import Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """검색 요청"""

    q: str = Field(..., min_length=2, max_length=200)
    catalog_id: str | None = Field(None, alias="catalogId")
    player_id: int | None = Field(None, alias="playerId")
    hand_grade: Literal["S", "A", "B", "C"] | None = Field(None, alias="handGrade")
    year: int | None = Field(None, ge=1970, le=2030)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: Literal["relevance", "date", "views"] = "relevance"

    class Config:
        populate_by_name = True


class SearchResultItem(BaseModel):
    """검색 결과 항목"""

    id: int
    title: str
    description: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    duration_sec: int = Field(alias="durationSec")
    view_count: int = Field(alias="viewCount")
    catalog_id: str = Field(alias="catalogId")
    series_title: str = Field(alias="seriesTitle")
    hands_count: int = Field(alias="handsCount")

    class Config:
        from_attributes = True
        populate_by_name = True


class SearchFacets(BaseModel):
    """검색 패싯"""

    catalogs: dict[str, int]
    players: dict[str, int]
    hand_grades: dict[str, int] = Field(alias="handGrades")
    years: dict[int, int]

    class Config:
        populate_by_name = True


class SearchResponse(BaseModel):
    """검색 응답"""

    results: list[SearchResultItem]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")
    facets: SearchFacets

    class Config:
        populate_by_name = True


class SuggestionItem(BaseModel):
    """자동완성 항목"""

    text: str
    type: Literal["content", "player", "series"]
    id: int | str


class SuggestResponse(BaseModel):
    """자동완성 응답"""

    suggestions: list[SuggestionItem]
