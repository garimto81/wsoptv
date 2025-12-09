"""
Jellyfin Service

Jellyfin API 통합 서비스
"""

from typing import Any

import httpx
from httpx import HTTPStatusError, RequestError

from ..core.config import settings
from ..schemas.jellyfin import (
    JellyfinContentListResponse,
    JellyfinContentResponse,
    JellyfinItem,
    JellyfinItemListResponse,
    JellyfinLibrary,
    JellyfinLibraryListResponse,
    JellyfinMediaSource,
    JellyfinPlaybackInfo,
    JellyfinServerInfo,
)


class JellyfinError(Exception):
    """Jellyfin API 에러"""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class JellyfinService:
    """Jellyfin API 클라이언트 서비스"""

    def __init__(self):
        self.host = settings.JELLYFIN_HOST
        self.api_key = settings.JELLYFIN_API_KEY
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        """API 요청 헤더"""
        return {
            "Authorization": settings.JELLYFIN_AUTH_HEADER,
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 (lazy initialization)"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.host,
                headers=self.headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """클라이언트 종료"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """API 요청 수행"""
        client = await self._get_client()
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            raise JellyfinError(
                f"Jellyfin API error: {e.response.text}",
                status_code=e.response.status_code,
            )
        except RequestError as e:
            raise JellyfinError(f"Connection error: {str(e)}")

    # =========================================================================
    # Server Info
    # =========================================================================

    async def get_server_info(self) -> JellyfinServerInfo:
        """서버 정보 조회"""
        data = await self._request("GET", "/System/Info")
        return JellyfinServerInfo(**data)

    async def get_public_info(self) -> dict[str, Any]:
        """공개 서버 정보 (인증 불필요)"""
        client = await self._get_client()
        response = await client.get("/System/Info/Public")
        return response.json()

    # =========================================================================
    # Libraries
    # =========================================================================

    async def get_libraries(self) -> list[JellyfinLibrary]:
        """라이브러리 목록 조회"""
        data = await self._request("GET", "/Library/MediaFolders")
        response = JellyfinLibraryListResponse(**data)
        return response.items

    async def get_library_by_name(self, name: str) -> JellyfinLibrary | None:
        """이름으로 라이브러리 조회"""
        libraries = await self.get_libraries()
        for lib in libraries:
            if lib.name.lower() == name.lower():
                return lib
        return None

    # =========================================================================
    # Items (Media Content)
    # =========================================================================

    async def get_items(
        self,
        parent_id: str | None = None,
        include_item_types: list[str] | None = None,
        recursive: bool = True,
        start_index: int = 0,
        limit: int = 20,
        sort_by: str = "DateCreated",
        sort_order: str = "Descending",
        search_term: str | None = None,
        fields: list[str] | None = None,
    ) -> JellyfinItemListResponse:
        """
        아이템 목록 조회

        Args:
            parent_id: 부모 폴더/라이브러리 ID
            include_item_types: 포함할 아이템 타입 (Movie, Episode, Video 등)
            recursive: 하위 폴더 포함 여부
            start_index: 시작 인덱스
            limit: 최대 결과 수
            sort_by: 정렬 기준 (DateCreated, SortName, PremiereDate 등)
            sort_order: 정렬 순서 (Ascending, Descending)
            search_term: 검색어
            fields: 포함할 필드 (Path, Overview, MediaSources 등)
        """
        params: dict[str, Any] = {
            "Recursive": str(recursive).lower(),
            "StartIndex": start_index,
            "Limit": limit,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }

        if parent_id:
            params["ParentId"] = parent_id

        if include_item_types:
            params["IncludeItemTypes"] = ",".join(include_item_types)

        if search_term:
            params["SearchTerm"] = search_term

        if fields:
            params["Fields"] = ",".join(fields)
        else:
            # 기본 필드
            params["Fields"] = "Path,Overview,DateCreated,MediaSources"

        data = await self._request("GET", "/Items", params=params)
        return JellyfinItemListResponse(**data)

    async def get_item(
        self,
        item_id: str,
        fields: list[str] | None = None,
    ) -> JellyfinItem:
        """
        단일 아이템 조회

        Note: Jellyfin 10.11+에서는 /Items/{id} 대신 /Items?Ids={id} 사용
        """
        params: dict[str, Any] = {"Ids": item_id}
        if fields:
            params["Fields"] = ",".join(fields)
        else:
            params["Fields"] = "Path,Overview,DateCreated,MediaSources"

        data = await self._request("GET", "/Items", params=params)
        items = data.get("Items", [])
        if not items:
            raise JellyfinError(f"Item not found: {item_id}", status_code=404)
        return JellyfinItem(**items[0])

    async def search_items(
        self,
        query: str,
        include_item_types: list[str] | None = None,
        limit: int = 20,
    ) -> JellyfinItemListResponse:
        """아이템 검색"""
        return await self.get_items(
            search_term=query,
            include_item_types=include_item_types or ["Movie", "Episode", "Video"],
            limit=limit,
            sort_by="SortName",
            sort_order="Ascending",
        )

    # =========================================================================
    # Playback
    # =========================================================================

    async def get_playback_info(self, item_id: str) -> JellyfinPlaybackInfo:
        """재생 정보 조회"""
        data = await self._request("GET", f"/Items/{item_id}/PlaybackInfo")
        return JellyfinPlaybackInfo(**data)

    def get_stream_url(
        self,
        item_id: str,
        media_source_id: str | None = None,
        static: bool = True,
    ) -> str:
        """HLS 스트림 URL 생성"""
        source_id = media_source_id or item_id
        params = f"Static={str(static).lower()}&mediaSourceId={source_id}&api_key={self.api_key}"
        return f"{self.host}/Videos/{item_id}/stream.m3u8?{params}"

    def get_direct_stream_url(self, item_id: str) -> str:
        """Direct Stream URL (트랜스코딩 없이)"""
        return f"{self.host}/Videos/{item_id}/stream?Static=true&api_key={self.api_key}"

    def get_thumbnail_url(
        self,
        item_id: str,
        image_type: str = "Primary",
        max_width: int | None = None,
        max_height: int | None = None,
    ) -> str:
        """썸네일 이미지 URL 생성"""
        url = f"{self.host}/Items/{item_id}/Images/{image_type}"
        params = []
        if max_width:
            params.append(f"maxWidth={max_width}")
        if max_height:
            params.append(f"maxHeight={max_height}")
        if params:
            url += "?" + "&".join(params)
        return url

    # =========================================================================
    # WSOPTV 통합 메서드
    # =========================================================================

    async def get_contents(
        self,
        library_name: str | None = None,
        page: int = 1,
        limit: int = 20,
        search_term: str | None = None,
    ) -> JellyfinContentListResponse:
        """
        WSOPTV 콘텐츠 목록 조회 (통합 API)

        기존 WSOPTV ContentListResponse 형식과 호환
        """
        # 라이브러리 ID 조회
        parent_id = None
        if library_name:
            library = await self.get_library_by_name(library_name)
            if library:
                parent_id = library.id

        # 아이템 조회
        start_index = (page - 1) * limit
        response = await self.get_items(
            parent_id=parent_id,
            include_item_types=["Movie", "Episode", "Video"],
            start_index=start_index,
            limit=limit,
            search_term=search_term,
            fields=["Path", "Overview", "DateCreated", "MediaSources"],
        )

        # WSOPTV 형식으로 변환
        items = [
            JellyfinContentResponse.from_jellyfin_item(
                item=item,
                jellyfin_host=self.host,
                api_key=self.api_key,
            )
            for item in response.items
        ]

        return JellyfinContentListResponse(
            items=items,
            total=response.total_record_count,
            page=page,
            limit=limit,
            has_next=(start_index + limit) < response.total_record_count,
        )

    async def get_content(self, item_id: str) -> JellyfinContentResponse:
        """단일 콘텐츠 조회 (WSOPTV 형식)"""
        item = await self.get_item(
            item_id,
            fields=["Path", "Overview", "DateCreated", "MediaSources"],
        )

        return JellyfinContentResponse.from_jellyfin_item(
            item=item,
            jellyfin_host=self.host,
            api_key=self.api_key,
        )


# Singleton instance
jellyfin_service = JellyfinService()
