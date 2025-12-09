"""
Stream API Router

HLS 스트리밍 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...core.deps import ActiveUser, DbSession
from ...models.content import Content
from ...services.streaming import streaming_service

router = APIRouter()


@router.get("/{content_id}/manifest.m3u8")
async def get_master_manifest(
    content_id: int,
    db: DbSession,
    _: ActiveUser,
) -> Response:
    """
    HLS 마스터 매니페스트

    - 🔒 인증 필요
    - 품질 옵션 제공
    """
    # Get content
    result = await db.execute(
        select(Content)
        .where(Content.id == content_id)
        .options(selectinload(Content.file))
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

    manifest = await streaming_service.generate_master_manifest(
        content_id=content_id,
        duration_sec=content.duration_sec,
    )

    return Response(
        content=manifest,
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/{content_id}/playlist_{quality}.m3u8")
async def get_quality_manifest(
    content_id: int,
    quality: str,
    db: DbSession,
    _: ActiveUser,
) -> Response:
    """
    품질별 HLS 매니페스트

    - 🔒 인증 필요
    """
    # Validate quality
    valid_qualities = ["360p", "480p", "720p", "1080p"]
    if quality not in valid_qualities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_QUALITY",
                "message": f"유효하지 않은 품질입니다. 가능한 값: {valid_qualities}",
            },
        )

    # Get content
    result = await db.execute(
        select(Content).where(Content.id == content_id)
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

    manifest = await streaming_service.generate_quality_manifest(
        content_id=content_id,
        duration_sec=content.duration_sec,
        quality=quality,
    )

    return Response(
        content=manifest,
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/{content_id}/segment_{segment_index:int}.ts")
async def get_segment(
    content_id: int,
    segment_index: int,
    db: DbSession,
    _: ActiveUser,
    quality: str = Query("720p", regex="^(360p|480p|720p|1080p)$"),
) -> StreamingResponse:
    """
    HLS 세그먼트 스트리밍

    - 🔒 인증 필요
    - On-demand 트랜스먹싱
    - 캐싱 지원
    """
    # Get content with file info
    result = await db.execute(
        select(Content)
        .where(Content.id == content_id)
        .options(selectinload(Content.file))
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

    if not content.file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FILE_NOT_FOUND",
                "message": "미디어 파일을 찾을 수 없습니다",
            },
        )

    # Validate segment index
    max_segments = (content.duration_sec + 5) // 6  # Approximate
    if segment_index < 0 or segment_index > max_segments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SEGMENT_NOT_FOUND",
                "message": "세그먼트를 찾을 수 없습니다",
            },
        )

    return StreamingResponse(
        streaming_service.get_segment(
            content_id=content_id,
            segment_index=segment_index,
            nas_path=content.file.nas_path,
            quality=quality,
        ),
        media_type="video/mp2t",
        headers={
            "Cache-Control": "max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/{content_id}/quality-options")
async def get_quality_options(
    content_id: int,
    db: DbSession,
    _: ActiveUser,
) -> dict:
    """
    사용 가능한 품질 옵션

    - 🔒 인증 필요
    """
    result = await db.execute(
        select(Content)
        .where(Content.id == content_id)
        .options(selectinload(Content.file))
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

    # Determine available qualities based on source resolution
    all_qualities = ["360p", "480p", "720p", "1080p"]
    available_qualities = []

    if content.file and content.file.resolution:
        # Parse resolution (e.g., "1920x1080")
        try:
            width = int(content.file.resolution.split("x")[0])
            if width >= 1920:
                available_qualities = all_qualities
            elif width >= 1280:
                available_qualities = ["360p", "480p", "720p"]
            elif width >= 854:
                available_qualities = ["360p", "480p"]
            else:
                available_qualities = ["360p"]
        except (ValueError, IndexError):
            available_qualities = all_qualities
    else:
        available_qualities = all_qualities

    return {
        "qualities": available_qualities,
        "default": "720p" if "720p" in available_qualities else available_qualities[-1],
    }
