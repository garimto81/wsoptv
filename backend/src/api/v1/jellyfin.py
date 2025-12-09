"""
Jellyfin API Router

Jellyfin 통합 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from ...core.deps import ActiveUser
from ...services.jellyfin import JellyfinError, JellyfinService
from ...schemas.jellyfin import (
    JellyfinContentListResponse,
    JellyfinContentResponse,
    JellyfinLibrary,
    JellyfinServerInfo,
)
from ...schemas.common import ApiResponse

router = APIRouter()

# Lazy-initialized service instance
_jellyfin_service: JellyfinService | None = None


def get_jellyfin_service() -> JellyfinService:
    """Get or create JellyfinService instance"""
    global _jellyfin_service
    if _jellyfin_service is None:
        _jellyfin_service = JellyfinService()
    return _jellyfin_service


# =============================================================================
# Server Info
# =============================================================================


@router.get("/server")
async def get_server_info(
    _: ActiveUser,
) -> ApiResponse[JellyfinServerInfo]:
    """
    Jellyfin 서버 정보

    - 🔒 인증 필요
    - 서버 이름, 버전, ID 반환
    """
    service = get_jellyfin_service()
    try:
        info = await service.get_server_info()
        return ApiResponse(data=info)
    except JellyfinError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "JELLYFIN_ERROR",
                "message": e.message,
            },
        )


# =============================================================================
# Libraries
# =============================================================================


@router.get("/libraries")
async def list_libraries(
    _: ActiveUser,
) -> ApiResponse[list[JellyfinLibrary]]:
    """
    Jellyfin 라이브러리 목록

    - 🔒 인증 필요
    - 모든 미디어 폴더 반환
    """
    service = get_jellyfin_service()
    try:
        libraries = await service.get_libraries()
        return ApiResponse(data=libraries)
    except JellyfinError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "JELLYFIN_ERROR",
                "message": e.message,
            },
        )


# =============================================================================
# Contents (WSOPTV Format)
# =============================================================================


@router.get("/contents")
async def list_contents(
    _: ActiveUser,
    library: str | None = Query(None, description="Library name (e.g., WSOP, HCL)"),
    q: str | None = Query(None, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ApiResponse[JellyfinContentListResponse]:
    """
    Jellyfin 콘텐츠 목록 (WSOPTV 형식)

    - 🔒 인증 필요
    - 라이브러리 필터링
    - 검색 지원
    - 페이지네이션 지원
    """
    service = get_jellyfin_service()
    try:
        contents = await service.get_contents(
            library_name=library,
            page=page,
            limit=limit,
            search_term=q,
        )
        return ApiResponse(data=contents)
    except JellyfinError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "JELLYFIN_ERROR",
                "message": e.message,
            },
        )


@router.get("/contents/{item_id}")
async def get_content(
    item_id: str,
    _: ActiveUser,
) -> ApiResponse[JellyfinContentResponse]:
    """
    Jellyfin 콘텐츠 상세 (WSOPTV 형식)

    - 🔒 인증 필요
    - 스트림 URL 포함
    - 썸네일 URL 포함
    """
    service = get_jellyfin_service()
    try:
        content = await service.get_content(item_id)
        return ApiResponse(data=content)
    except JellyfinError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "JELLYFIN_ERROR",
                "message": e.message,
            },
        )


# =============================================================================
# Streaming
# =============================================================================


@router.get("/stream/{item_id}", response_model=None)
async def get_stream_url(
    item_id: str,
    _: ActiveUser,
    redirect: bool = Query(False, description="Redirect to stream URL"),
):
    """
    Jellyfin 스트림 URL 조회

    - 🔒 인증 필요
    - HLS 스트림 URL 반환
    - redirect=true 시 스트림으로 리다이렉트
    """
    service = get_jellyfin_service()

    stream_url = service.get_stream_url(item_id)
    direct_url = service.get_direct_stream_url(item_id)

    if redirect:
        return RedirectResponse(url=stream_url)

    return {
        "item_id": item_id,
        "hls_url": stream_url,
        "direct_url": direct_url,
        "thumbnail_url": service.get_thumbnail_url(item_id),
    }


@router.get("/thumbnail/{item_id}")
async def get_thumbnail(
    item_id: str,
    width: int | None = Query(None, ge=1, le=1920),
    height: int | None = Query(None, ge=1, le=1080),
) -> RedirectResponse:
    """
    Jellyfin 썸네일 이미지 (리다이렉트)

    - 인증 불필요 (Jellyfin이 처리)
    - 크기 조절 가능
    """
    service = get_jellyfin_service()
    thumbnail_url = service.get_thumbnail_url(
        item_id,
        max_width=width,
        max_height=height,
    )
    return RedirectResponse(url=thumbnail_url)


# =============================================================================
# Search
# =============================================================================


@router.get("/search")
async def search_contents(
    _: ActiveUser,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> ApiResponse[JellyfinContentListResponse]:
    """
    Jellyfin 콘텐츠 검색

    - 🔒 인증 필요
    - 제목, 개요에서 검색
    """
    service = get_jellyfin_service()
    try:
        result = await service.search_items(
            query=q,
            include_item_types=["Movie", "Episode", "Video"],
            limit=limit,
        )

        # Convert to WSOPTV format
        from ...schemas.jellyfin import JellyfinContentResponse

        items = [
            JellyfinContentResponse.from_jellyfin_item(
                item=item,
                jellyfin_host=service.host,
                api_key=service.api_key,
            )
            for item in result.items
        ]

        return ApiResponse(
            data=JellyfinContentListResponse(
                items=items,
                total=result.total_record_count,
                page=1,
                limit=limit,
                has_next=len(items) < result.total_record_count,
            )
        )
    except JellyfinError as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "JELLYFIN_ERROR",
                "message": e.message,
            },
        )
