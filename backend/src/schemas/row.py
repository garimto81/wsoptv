"""
Row Schemas

Netflix-style 동적 카탈로그 Row 시스템을 위한 스키마 정의
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RowType(str, Enum):
    """Row 타입"""

    RECENTLY_ADDED = "recently_added"
    LIBRARY = "library"  # 레거시: Jellyfin Library 기반
    SERIES = "series"  # 신규: PostgreSQL series 테이블 기반
    CATALOG = "catalog"  # 신규: PostgreSQL catalog 그룹
    CONTINUE_WATCHING = "continue_watching"
    TRENDING = "trending"
    TOP_RATED = "top_rated"
    TAG = "tag"


class RowItem(BaseModel):
    """Row 내 개별 아이템"""

    id: str = Field(description="Jellyfin Item ID 또는 Content ID")
    title: str
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    duration_sec: int = Field(alias="durationSec", default=0)
    library_name: str | None = Field(None, alias="libraryName")  # 레거시 호환
    series_name: str | None = Field(None, alias="seriesName")  # 신규: Series 이름
    progress: int | None = Field(None, description="시청 진행률 (0-100)")
    year: int | None = None
    date_created: datetime | None = Field(None, alias="dateCreated")

    class Config:
        populate_by_name = True


class RowFilter(BaseModel):
    """Row 필터 정보"""

    library_id: str | None = Field(None, alias="libraryId")  # 레거시: Jellyfin Library ID
    series_id: int | None = Field(None, alias="seriesId")  # 신규: PostgreSQL Series ID
    catalog_id: str | None = Field(None, alias="catalogId")  # 신규: PostgreSQL Catalog ID
    sort_by: str | None = Field(None, alias="sortBy")
    sort_order: str | None = Field(None, alias="sortOrder")
    limit: int | None = None

    class Config:
        populate_by_name = True


class RowData(BaseModel):
    """Row 데이터"""

    id: str = Field(description="Row 고유 ID")
    type: RowType = Field(description="Row 타입")
    title: str = Field(description="표시 제목")
    items: list[RowItem] = Field(default_factory=list)
    filter: RowFilter | None = None
    view_all_url: str = Field(alias="viewAllUrl", description="View All 링크")
    total_count: int = Field(0, alias="totalCount", description="전체 아이템 수")

    class Config:
        populate_by_name = True


class HomeRowsResponse(BaseModel):
    """홈페이지 Row 목록 응답"""

    rows: list[RowData]
    cached: bool = False
    cache_expires_at: datetime | None = Field(None, alias="cacheExpiresAt")

    class Config:
        populate_by_name = True


class BrowseParams(BaseModel):
    """Browse 페이지 요청 파라미터"""

    library_id: str | None = Field(None, alias="libraryId")  # 레거시: Jellyfin Library ID
    series_id: int | None = Field(None, alias="seriesId")  # 신규: PostgreSQL Series ID
    catalog_id: str | None = Field(None, alias="catalogId")  # 신규: PostgreSQL Catalog ID
    sort_by: str = Field("DateCreated", alias="sortBy")
    sort_order: str = Field("Descending", alias="sortOrder")
    page: int = 1
    limit: int = 20
    search: str | None = None

    class Config:
        populate_by_name = True


class BrowseResponse(BaseModel):
    """Browse 페이지 응답"""

    items: list[RowItem]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True
