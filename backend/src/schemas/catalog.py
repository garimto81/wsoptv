"""
Catalog Schemas

카탈로그 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field


class CatalogResponse(BaseModel):
    """카탈로그 응답"""

    id: str
    name: str
    display_title: str = Field(alias="displayTitle")
    description: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    series_count: int = Field(0, alias="seriesCount")
    content_count: int = Field(0, alias="contentCount")

    class Config:
        from_attributes = True
        populate_by_name = True


class CatalogListResponse(BaseModel):
    """카탈로그 목록 응답"""

    items: list[CatalogResponse]
    total: int


class SeriesSummary(BaseModel):
    """시리즈 요약 (카탈로그 상세용)"""

    id: int
    title: str
    year: int
    episode_count: int = Field(alias="episodeCount")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")

    class Config:
        from_attributes = True
        populate_by_name = True


class CatalogDetailResponse(BaseModel):
    """카탈로그 상세 응답"""

    id: str
    name: str
    display_title: str = Field(alias="displayTitle")
    description: str | None = None
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    series: list[SeriesSummary]

    class Config:
        from_attributes = True
        populate_by_name = True
