"""
Row Service

Netflix-style 동적 카탈로그 Row 생성 서비스

핵심 원칙 (v2.0 - Hybrid Architecture):
- USE_HYBRID_CATALOG=true: PostgreSQL catalogs/series 기반 Row 생성
- USE_HYBRID_CATALOG=false: Jellyfin Library 기반 Row 생성 (레거시)
- Redis 캐싱 필수 (TTL 5분)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import settings
from ..core.database import async_session_maker
from ..models.catalog import Catalog
from ..models.content import Content
from ..models.series import Series
from ..schemas.jellyfin import JellyfinItem
from ..schemas.row import (
    BrowseParams,
    BrowseResponse,
    HomeRowsResponse,
    RowData,
    RowFilter,
    RowItem,
    RowType,
)
from .jellyfin import JellyfinError, JellyfinService, jellyfin_service

logger = logging.getLogger(__name__)

# Cache TTL (seconds)
CACHE_TTL_ROWS = 300  # 5분
CACHE_TTL_LIBRARY = 300  # 5분
CACHE_TTL_TRENDING = 3600  # 1시간


class RowService:
    """
    동적 Row 생성 서비스

    Jellyfin API를 호출하여 Row 데이터를 동적으로 생성합니다.
    캐시는 현재 인메모리로 구현 (추후 Redis 전환)
    """

    def __init__(self, jellyfin: JellyfinService):
        self.jellyfin = jellyfin
        self._cache: dict[str, tuple[Any, datetime]] = {}

    def _get_cache(self, key: str) -> Any | None:
        """캐시 조회"""
        if key in self._cache:
            data, expires_at = self._cache[key]
            if datetime.now(timezone.utc) < expires_at:
                return data
            del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any, ttl: int) -> None:
        """캐시 저장"""
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        self._cache[key] = (data, expires_at)

    def _get_cache_expires_at(self, key: str) -> datetime | None:
        """캐시 만료 시간 조회"""
        if key in self._cache:
            _, expires_at = self._cache[key]
            return expires_at
        return None

    def _jellyfin_item_to_row_item(
        self,
        item: JellyfinItem,
        library_name: str | None = None,
    ) -> RowItem:
        """Jellyfin Item을 RowItem으로 변환"""
        # 썸네일 URL 생성
        thumbnail_url = None
        if item.image_tags and item.image_tags.primary:
            thumbnail_url = self.jellyfin.get_thumbnail_url(
                item.id, "Primary", max_width=400
            )

        return RowItem(
            id=item.id,
            title=item.name,
            thumbnail_url=thumbnail_url,
            duration_sec=item.duration_seconds,
            library_name=library_name or item.series_name,
            year=item.production_year,
            date_created=item.date_created,
        )

    async def get_homepage_rows(
        self,
        user_id: int | None = None,
        limit_per_row: int = 20,
    ) -> HomeRowsResponse:
        """
        홈페이지 Row 목록 조회

        Args:
            user_id: 사용자 ID (로그인 시 Continue Watching 포함)
            limit_per_row: Row당 아이템 수

        Returns:
            HomeRowsResponse: Row 목록
        """
        cache_key = f"wsoptv:home:rows:{user_id or 'anonymous'}"
        cached = self._get_cache(cache_key)
        if cached:
            logger.info(f"Cache hit: {cache_key}")
            return HomeRowsResponse(
                rows=cached,
                cached=True,
                cache_expires_at=self._get_cache_expires_at(cache_key),
            )

        rows: list[RowData] = []

        try:
            # 1. Recently Added Row
            recently_added = await self._build_recently_added_row(limit_per_row)
            if recently_added.items:
                rows.append(recently_added)

            # 2. Content Rows (Feature Flag 분기)
            if settings.USE_HYBRID_CATALOG:
                # 신규: PostgreSQL catalogs/series 기반 Row
                logger.info("Using Hybrid Catalog (PostgreSQL series-based rows)")
                series_rows = await self._build_series_rows(limit_per_row)
                rows.extend([r for r in series_rows if r.items])
            else:
                # 레거시: Jellyfin Library 기반 Row
                logger.info("Using Legacy Catalog (Jellyfin library-based rows)")
                library_rows = await self._build_library_rows(limit_per_row)
                rows.extend([r for r in library_rows if r.items])

            # 3. Continue Watching (로그인 사용자만)
            # TODO: user_id로 watch_progress 조회 구현

            # 4. Trending Row
            # TODO: view_events 기반 인기 콘텐츠 구현

            # 캐시 저장
            self._set_cache(cache_key, rows, CACHE_TTL_ROWS)

            return HomeRowsResponse(
                rows=rows,
                cached=False,
                cache_expires_at=self._get_cache_expires_at(cache_key),
            )

        except JellyfinError as e:
            logger.error(f"Jellyfin error: {e.message}")
            # Fallback: 만료된 캐시라도 반환
            stale_key = f"wsoptv:home:rows:stale"
            stale_cache = self._get_cache(stale_key)
            if stale_cache:
                return HomeRowsResponse(rows=stale_cache, cached=True)
            return HomeRowsResponse(rows=[], cached=False)

    async def _build_recently_added_row(self, limit: int) -> RowData:
        """Recently Added Row 생성"""
        response = await self.jellyfin.get_items(
            include_item_types=["Movie", "Episode", "Video"],
            sort_by="DateCreated",
            sort_order="Descending",
            limit=limit,
        )

        items = [
            self._jellyfin_item_to_row_item(item)
            for item in response.items
        ]

        return RowData(
            id="recently_added",
            type=RowType.RECENTLY_ADDED,
            title="Recently Added",
            items=items,
            view_all_url="/browse?sort=DateCreated&order=desc",
            total_count=response.total_record_count,
            filter=RowFilter(sort_by="DateCreated", sort_order="Descending"),
        )

    async def _build_series_rows(self, limit: int) -> list[RowData]:
        """
        PostgreSQL series 테이블 기반 Row 생성 (하이브리드 모드)

        Series를 Catalog 순서, Year 내림차순으로 정렬하여 Row 생성
        """
        rows: list[RowData] = []

        async with async_session_maker() as session:
            # Series 목록 조회 (Catalog 순서, Year 내림차순)
            stmt = (
                select(Series)
                .join(Catalog)
                .options(selectinload(Series.catalog))
                .order_by(Catalog.sort_order, Series.year.desc())
            )
            result = await session.execute(stmt)
            series_list = result.scalars().all()

            for series in series_list:
                cache_key = f"wsoptv:home:series:{series.id}"
                cached = self._get_cache(cache_key)

                if cached:
                    rows.append(cached)
                    continue

                # Series별 콘텐츠 조회
                content_stmt = (
                    select(Content)
                    .where(Content.series_id == series.id)
                    .order_by(Content.episode_num.asc().nullsfirst())
                    .limit(limit)
                )
                content_result = await session.execute(content_stmt)
                contents = content_result.scalars().all()

                if not contents:
                    continue

                # Content → RowItem 변환
                items = [
                    self._content_to_row_item(content, series.title)
                    for content in contents
                ]

                # 전체 콘텐츠 수 조회
                from sqlalchemy import func
                count_stmt = (
                    select(func.count())
                    .select_from(Content)
                    .where(Content.series_id == series.id)
                )
                count_result = await session.execute(count_stmt)
                total_count = count_result.scalar() or 0

                row = RowData(
                    id=f"series_{series.id}",
                    type=RowType.SERIES,
                    title=series.title,
                    items=items,
                    view_all_url=f"/browse?series={series.id}",
                    total_count=total_count,
                    filter=RowFilter(
                        series_id=series.id,
                        sort_by="episode_num",
                        sort_order="Ascending",
                    ),
                )

                # 캐시 저장
                self._set_cache(cache_key, row, CACHE_TTL_LIBRARY)
                rows.append(row)

        return rows

    def _content_to_row_item(
        self,
        content: Content,
        series_name: str | None = None,
    ) -> RowItem:
        """PostgreSQL Content를 RowItem으로 변환"""
        return RowItem(
            id=content.file_id or str(content.id),
            title=content.title,
            thumbnail_url=content.thumbnail_url,
            duration_sec=content.duration_sec,
            series_name=series_name,
            year=None,  # Content 모델에 year 필드 없음
            date_created=content.created_at,
        )

    async def _build_library_rows(self, limit: int) -> list[RowData]:
        """라이브러리별 Row 동적 생성 (레거시 - Jellyfin Library 기반)"""
        rows: list[RowData] = []

        # 라이브러리 목록 조회
        libraries = await self.jellyfin.get_libraries()

        for library in libraries:
            cache_key = f"wsoptv:home:library:{library.id}"
            cached = self._get_cache(cache_key)

            if cached:
                rows.append(cached)
                continue

            # 라이브러리별 아이템 조회
            response = await self.jellyfin.get_items(
                parent_id=library.id,
                include_item_types=["Movie", "Episode", "Video"],
                sort_by="DateCreated",
                sort_order="Descending",
                limit=limit,
            )

            if not response.items:
                continue

            items = [
                self._jellyfin_item_to_row_item(item, library.name)
                for item in response.items
            ]

            row = RowData(
                id=f"library_{library.id}",
                type=RowType.LIBRARY,
                title=library.name,
                items=items,
                view_all_url=f"/browse?library={library.id}",
                total_count=response.total_record_count,
                filter=RowFilter(
                    library_id=library.id,
                    sort_by="DateCreated",
                    sort_order="Descending",
                ),
            )

            # 캐시 저장
            self._set_cache(cache_key, row, CACHE_TTL_LIBRARY)
            rows.append(row)

        return rows

    async def get_library_row(
        self,
        library_id: str,
        limit: int = 20,
    ) -> RowData | None:
        """특정 라이브러리 Row 조회"""
        library = await self.jellyfin.get_library_by_id(library_id)
        if not library:
            return None

        response = await self.jellyfin.get_items(
            parent_id=library_id,
            include_item_types=["Movie", "Episode", "Video"],
            sort_by="DateCreated",
            sort_order="Descending",
            limit=limit,
        )

        items = [
            self._jellyfin_item_to_row_item(item, library.name)
            for item in response.items
        ]

        return RowData(
            id=f"library_{library_id}",
            type=RowType.LIBRARY,
            title=library.name,
            items=items,
            view_all_url=f"/browse?library={library_id}",
            total_count=response.total_record_count,
        )

    async def get_browse_contents(
        self,
        params: BrowseParams,
    ) -> BrowseResponse:
        """Browse 페이지 콘텐츠 조회 (필터링/정렬/페이지네이션)"""

        # Series/Catalog 필터가 있으면 PostgreSQL 기반 조회 (하이브리드 모드)
        if params.series_id or params.catalog_id:
            return await self._get_browse_contents_from_db(params)

        # 기존: Jellyfin Library 기반 조회
        return await self._get_browse_contents_from_jellyfin(params)

    async def _get_browse_contents_from_jellyfin(
        self,
        params: BrowseParams,
    ) -> BrowseResponse:
        """Jellyfin 기반 Browse 콘텐츠 조회 (레거시)"""
        start_index = (params.page - 1) * params.limit

        response = await self.jellyfin.get_items(
            parent_id=params.library_id,
            include_item_types=["Movie", "Episode", "Video"],
            start_index=start_index,
            limit=params.limit,
            sort_by=params.sort_by,
            sort_order=params.sort_order,
            search_term=params.search,
        )

        # 라이브러리 이름 조회
        library_name = None
        if params.library_id:
            library = await self.jellyfin.get_library_by_id(params.library_id)
            library_name = library.name if library else None

        items = [
            self._jellyfin_item_to_row_item(item, library_name)
            for item in response.items
        ]

        has_next = (start_index + params.limit) < response.total_record_count

        return BrowseResponse(
            items=items,
            total=response.total_record_count,
            page=params.page,
            limit=params.limit,
            has_next=has_next,
        )

    async def _get_browse_contents_from_db(
        self,
        params: BrowseParams,
    ) -> BrowseResponse:
        """PostgreSQL 기반 Browse 콘텐츠 조회 (하이브리드 모드)"""
        from sqlalchemy import func

        offset = (params.page - 1) * params.limit

        async with async_session_maker() as session:
            # 기본 쿼리
            stmt = select(Content).options(selectinload(Content.series))

            # Series 필터
            if params.series_id:
                stmt = stmt.where(Content.series_id == params.series_id)

            # Catalog 필터 (해당 Catalog의 모든 Series 포함)
            if params.catalog_id:
                series_ids_stmt = select(Series.id).where(Series.catalog_id == params.catalog_id)
                stmt = stmt.where(Content.series_id.in_(series_ids_stmt))

            # 정렬
            if params.sort_by == "DateCreated":
                order_col = Content.created_at
            elif params.sort_by == "SortName":
                order_col = Content.title
            else:
                order_col = Content.episode_num

            if params.sort_order == "Descending":
                stmt = stmt.order_by(order_col.desc().nullsfirst())
            else:
                stmt = stmt.order_by(order_col.asc().nullsfirst())

            # 페이지네이션
            stmt = stmt.offset(offset).limit(params.limit)

            # 실행
            result = await session.execute(stmt)
            contents = result.scalars().all()

            # 전체 수 조회
            count_stmt = select(func.count()).select_from(Content)
            if params.series_id:
                count_stmt = count_stmt.where(Content.series_id == params.series_id)
            if params.catalog_id:
                series_ids_stmt = select(Series.id).where(Series.catalog_id == params.catalog_id)
                count_stmt = count_stmt.where(Content.series_id.in_(series_ids_stmt))

            count_result = await session.execute(count_stmt)
            total = count_result.scalar() or 0

            # RowItem 변환
            items = []
            for content in contents:
                series_name = content.series.title if content.series else None
                items.append(self._content_to_row_item(content, series_name))

            has_next = (offset + params.limit) < total

            return BrowseResponse(
                items=items,
                total=total,
                page=params.page,
                limit=params.limit,
                has_next=has_next,
            )


# Singleton instance
row_service = RowService(jellyfin_service)
