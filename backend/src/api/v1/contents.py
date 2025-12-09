"""
Contents API Router

콘텐츠 관련 API 엔드포인트 (시리즈, 콘텐츠, 핸드)
"""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ...core.config import settings
from ...core.deps import ActiveUser, DbSession
from ...models.content import Content
from ...models.hand import Hand
from ...models.series import Series
from ...schemas.common import ApiResponse, PaginatedResponse
from ...schemas.content import (
    ContentDetailResponse,
    ContentListResponse,
    ContentResponse,
    HandSummary,
    SeriesInfo,
)
from ...schemas.hand import HandListResponse, HandResponse
from ...schemas.series import ContentSummary, SeriesDetailResponse, SeriesResponse

router = APIRouter()


# ============================================================================
# Series Endpoints
# ============================================================================


@router.get("/series/{series_id}")
async def get_series(
    series_id: int,
    db: DbSession,
    _: ActiveUser,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ApiResponse[SeriesDetailResponse]:
    """
    시리즈 상세 + 콘텐츠 목록

    - 🔒 인증 필요
    - 페이지네이션 지원
    """
    # Get series
    result = await db.execute(
        select(Series)
        .where(Series.id == series_id)
        .options(selectinload(Series.contents).selectinload(Content.hands))
    )
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SERIES_NOT_FOUND",
                "message": "시리즈를 찾을 수 없습니다",
            },
        )

    # Paginate contents
    all_contents = series.contents
    total = len(all_contents)
    offset = (page - 1) * limit
    paginated_contents = all_contents[offset : offset + limit]

    content_items = [
        ContentSummary(
            id=c.id,
            episode_num=c.episode_num,
            title=c.title,
            duration_sec=c.duration_sec,
            thumbnail_url=c.thumbnail_url,
            view_count=c.view_count,
            hands_count=len(c.hands),
        )
        for c in paginated_contents
    ]

    return ApiResponse(
        data=SeriesDetailResponse(
            id=series.id,
            catalog_id=series.catalog_id,
            title=series.title,
            year=series.year,
            season_num=series.season_num,
            description=series.description,
            thumbnail_url=series.thumbnail_url,
            episode_count=total,
            contents=PaginatedResponse(
                items=content_items,
                total=total,
                page=page,
                limit=limit,
                has_next=(offset + limit) < total,
            ),
        )
    )


# ============================================================================
# Content Endpoints
# ============================================================================


@router.get("/contents")
async def list_contents(
    db: DbSession,
    _: ActiveUser,
    catalog_id: str | None = Query(None),
    series_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ApiResponse[ContentListResponse]:
    """
    콘텐츠 목록

    - 🔒 인증 필요
    - 카탈로그/시리즈 필터링
    - 페이지네이션 지원
    """
    query = select(Content).options(
        selectinload(Content.series),
        selectinload(Content.hands),
    )

    if series_id:
        query = query.where(Content.series_id == series_id)
    elif catalog_id:
        query = query.join(Series).where(Series.catalog_id == catalog_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Content.created_at.desc())

    result = await db.execute(query)
    contents = result.scalars().all()

    items = [
        ContentResponse(
            id=c.id,
            series_id=c.series_id,
            episode_num=c.episode_num,
            title=c.title,
            description=c.description,
            duration_sec=c.duration_sec,
            thumbnail_url=c.thumbnail_url,
            view_count=c.view_count,
            hands_count=len(c.hands),
            created_at=c.created_at,
        )
        for c in contents
    ]

    return ApiResponse(
        data=ContentListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
    )


@router.get("/contents/{content_id}")
async def get_content(
    content_id: int,
    db: DbSession,
    _: ActiveUser,
) -> ApiResponse[ContentDetailResponse]:
    """
    콘텐츠 상세

    - 🔒 인증 필요
    - 시리즈 정보, 핸드 목록 포함
    - 스트리밍 URL 포함
    """
    result = await db.execute(
        select(Content)
        .where(Content.id == content_id)
        .options(
            selectinload(Content.series),
            selectinload(Content.hands),
            selectinload(Content.file),
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTENT_NOT_FOUND",
                "message": "콘텐츠를 찾을 수 없습니다",
            },
        )

    # Increment view count
    content.view_count += 1

    # Build stream URL
    stream_url = f"{settings.API_V1_PREFIX}/stream/{content_id}/manifest.m3u8"

    # Build hands list
    hands = [
        HandSummary(
            id=h.id,
            hand_number=h.hand_number,
            start_sec=h.start_sec,
            end_sec=h.end_sec,
            grade=h.grade,
            players=h.player_names,
            is_all_in=h.is_all_in,
        )
        for h in content.hands
    ]

    return ApiResponse(
        data=ContentDetailResponse(
            id=content.id,
            title=content.title,
            description=content.description,
            duration_sec=content.duration_sec,
            thumbnail_url=content.thumbnail_url,
            view_count=content.view_count,
            episode_num=content.episode_num,
            series=SeriesInfo(
                id=content.series.id,
                catalog_id=content.series.catalog_id,
                title=content.series.title,
                year=content.series.year,
            ),
            stream_url=stream_url,
            hands=hands,
            hands_count=len(hands),
        )
    )


# ============================================================================
# Hands Endpoints
# ============================================================================


@router.get("/contents/{content_id}/hands")
async def list_hands(
    content_id: int,
    db: DbSession,
    _: ActiveUser,
    grade: str | None = Query(None, regex="^[SABC]$"),
) -> ApiResponse[HandListResponse]:
    """
    콘텐츠의 핸드 목록

    - 🔒 인증 필요
    - 등급 필터링 가능
    """
    query = (
        select(Hand)
        .where(Hand.content_id == content_id)
        .options(selectinload(Hand.players))
        .order_by(Hand.start_sec)
    )

    if grade:
        query = query.where(Hand.grade == grade)

    result = await db.execute(query)
    hands = result.scalars().all()

    items = [
        HandResponse(
            id=h.id,
            content_id=h.content_id,
            hand_number=h.hand_number,
            start_sec=h.start_sec,
            end_sec=h.end_sec,
            winner=h.winner,
            pot_size_bb=h.pot_size_bb,
            is_all_in=h.is_all_in,
            is_showdown=h.is_showdown,
            board=h.board,
            grade=h.grade,
            tags=[],  # TODO: Parse JSON tags
            highlight_score=h.highlight_score,
            players=h.player_names,
        )
        for h in hands
    ]

    return ApiResponse(
        data=HandListResponse(
            items=items,
            total=len(items),
        )
    )


@router.get("/players")
async def list_players(
    db: DbSession,
    _: ActiveUser,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, min_length=1),
) -> ApiResponse[dict]:
    """
    플레이어 목록

    - 🔒 인증 필요
    - 검색 가능
    """
    from ...models.player import Player
    from ...schemas.player import PlayerListResponse, PlayerResponse

    query = select(Player)

    if q:
        query = query.where(Player.name.ilike(f"%{q}%"))

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Player.total_hands.desc())

    result = await db.execute(query)
    players = result.scalars().all()

    items = [
        PlayerResponse(
            id=p.id,
            name=p.name,
            display_name=p.display_name,
            country=p.country,
            avatar_url=p.avatar_url,
            total_hands=p.total_hands,
            total_wins=p.total_wins,
            win_rate=p.win_rate,
        )
        for p in players
    ]

    return ApiResponse(
        data=PlayerListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
    )
