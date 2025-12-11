"""
Home API Router

Netflix-style 동적 카탈로그 홈페이지 API
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from ...schemas.row import (
    BrowseParams,
    BrowseResponse,
    HomeRowsResponse,
    RowData,
)
from ...services.jellyfin import JellyfinError
from ...services.row_service import row_service

router = APIRouter()


@router.get(
    "",
    response_model=HomeRowsResponse,
    summary="홈페이지 Row 목록",
    description="""
    Netflix 스타일의 동적 Row 목록을 반환합니다.

    Row 타입:
    - `recently_added`: 최근 추가된 콘텐츠
    - `library`: Jellyfin 라이브러리별 콘텐츠
    - `continue_watching`: 이어보기 (로그인 필요)
    - `trending`: 인기 콘텐츠

    캐싱:
    - Row 데이터는 5분간 캐싱됩니다
    - `cached` 필드로 캐시 여부 확인 가능
    """,
)
async def get_homepage_rows(
    limit: Annotated[int, Query(ge=1, le=50, description="Row당 아이템 수")] = 20,
) -> HomeRowsResponse:
    """홈페이지 Row 목록 조회"""
    try:
        # TODO: 인증된 사용자의 경우 user_id 전달 (Continue Watching용)
        return await row_service.get_homepage_rows(
            user_id=None,
            limit_per_row=limit,
        )
    except JellyfinError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "JELLYFIN_UNAVAILABLE",
                "message": f"Jellyfin 서버에 연결할 수 없습니다: {e.message}",
            },
        )


@router.get(
    "/library/{library_id}",
    response_model=RowData | None,
    summary="특정 라이브러리 Row",
    description="특정 라이브러리의 Row 데이터를 반환합니다.",
)
async def get_library_row(
    library_id: str,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> RowData | None:
    """특정 라이브러리 Row 조회"""
    try:
        row = await row_service.get_library_row(library_id, limit)
        if not row:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "INVALID_LIBRARY",
                    "message": f"라이브러리를 찾을 수 없습니다: {library_id}",
                },
            )
        return row
    except JellyfinError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "JELLYFIN_UNAVAILABLE",
                "message": f"Jellyfin 서버에 연결할 수 없습니다: {e.message}",
            },
        )


@router.get(
    "/browse",
    response_model=BrowseResponse,
    summary="Browse 콘텐츠",
    description="""
    필터링/정렬/페이지네이션을 지원하는 콘텐츠 목록을 반환합니다.

    필터 옵션:
    - `library`: Jellyfin Library ID (레거시)
    - `series`: PostgreSQL Series ID (하이브리드 모드)
    - `catalog`: PostgreSQL Catalog ID (하이브리드 모드)

    정렬 옵션:
    - `DateCreated`: 추가일 기준
    - `SortName`: 이름 기준
    - `PremiereDate`: 방영일 기준
    - `CommunityRating`: 평점 기준
    """,
)
async def get_browse_contents(
    library_id: Annotated[str | None, Query(alias="library")] = None,
    series_id: Annotated[int | None, Query(alias="series")] = None,
    catalog_id: Annotated[str | None, Query(alias="catalog")] = None,
    sort_by: Annotated[str, Query(alias="sort")] = "DateCreated",
    sort_order: Annotated[str, Query(alias="order")] = "Descending",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(alias="q")] = None,
) -> BrowseResponse:
    """Browse 페이지 콘텐츠 조회"""
    try:
        params = BrowseParams(
            library_id=library_id,
            series_id=series_id,
            catalog_id=catalog_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
            search=search,
        )
        return await row_service.get_browse_contents(params)
    except JellyfinError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "JELLYFIN_UNAVAILABLE",
                "message": f"Jellyfin 서버에 연결할 수 없습니다: {e.message}",
            },
        )
