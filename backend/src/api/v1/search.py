"""
Search API Router

검색 관련 API 엔드포인트
"""

from fastapi import APIRouter, Query

from ...core.deps import ActiveUser
from ...schemas.common import ApiResponse
from ...schemas.search import (
    SearchFacets,
    SearchResponse,
    SearchResultItem,
    SuggestionItem,
    SuggestResponse,
)
from ...services.search import search_service

router = APIRouter()


@router.get("")
async def search(
    _: ActiveUser,
    q: str = Query(..., min_length=2, max_length=200),
    catalog_id: str | None = Query(None, alias="catalogId"),
    player_id: int | None = Query(None, alias="playerId"),
    hand_grade: str | None = Query(None, alias="handGrade", regex="^[SABC]$"),
    year: int | None = Query(None, ge=1970, le=2030),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("relevance", regex="^(relevance|date|views)$"),
) -> ApiResponse[SearchResponse]:
    """
    통합 검색

    - 🔒 인증 필요
    - MeiliSearch 기반 전문 검색
    - 패싯 필터링 지원
    """
    filters = {
        "catalog_id": catalog_id,
        "player_id": player_id,
        "hand_grade": hand_grade,
        "year": year,
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    result = await search_service.search(
        query=q,
        index_name="contents",
        filters=filters if filters else None,
        page=page,
        limit=limit,
        sort=sort,
    )

    # Convert results to response schema
    items = [
        SearchResultItem(
            id=hit.get("id", 0),
            title=hit.get("title", ""),
            description=hit.get("description"),
            thumbnail_url=hit.get("thumbnail_url"),
            duration_sec=hit.get("duration_sec", 0),
            view_count=hit.get("view_count", 0),
            catalog_id=hit.get("catalog_id", ""),
            series_title=hit.get("series_title", ""),
            hands_count=hit.get("hands_count", 0),
        )
        for hit in result.get("results", [])
    ]

    facets_data = result.get("facets", {})
    facets = SearchFacets(
        catalogs=facets_data.get("catalog_id", {}),
        players=facets_data.get("player_names", {}),
        hand_grades=facets_data.get("grade", {}),
        years={int(k): v for k, v in facets_data.get("year", {}).items()},
    )

    total = result.get("total", 0)
    has_next = ((page - 1) * limit + len(items)) < total

    return ApiResponse(
        data=SearchResponse(
            results=items,
            total=total,
            page=page,
            limit=limit,
            has_next=has_next,
            facets=facets,
        )
    )


@router.get("/suggest")
async def suggest(
    _: ActiveUser,
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=20),
) -> ApiResponse[SuggestResponse]:
    """
    자동완성 제안

    - 🔒 인증 필요
    - 콘텐츠 + 플레이어 검색
    """
    suggestions = await search_service.suggest(query=q, limit=limit)

    items = [
        SuggestionItem(
            text=s["text"],
            type=s["type"],
            id=s["id"],
        )
        for s in suggestions
    ]

    return ApiResponse(data=SuggestResponse(suggestions=items))
