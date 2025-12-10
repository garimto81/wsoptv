"""
Row Service

Netflix-style 동적 카탈로그 Row 생성 서비스

핵심 원칙:
- PostgreSQL에 카탈로그 데이터 저장 X (동적 생성)
- Jellyfin API를 통해 런타임에 Row 생성
- Redis 캐싱 필수 (TTL 5분)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from ..core.config import settings
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

            # 2. Library Rows (동적 생성)
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

    async def _build_library_rows(self, limit: int) -> list[RowData]:
        """라이브러리별 Row 동적 생성"""
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


# Singleton instance
row_service = RowService(jellyfin_service)
