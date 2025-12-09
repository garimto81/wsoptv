"""
Users API Router

사용자 데이터 관련 API 엔드포인트 (시청 진행, 기록)
"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from ...core.deps import ActiveUser, DbSession
from ...models.content import Content
from ...models.user import User, ViewEvent, WatchProgress
from ...schemas.common import ApiResponse

router = APIRouter()


# ============================================================================
# Schemas (local to this module)
# ============================================================================


class WatchProgressRequest(BaseModel):
    """시청 진행 저장 요청"""

    content_id: int = Field(alias="contentId")
    progress_sec: int = Field(alias="progressSec", ge=0)
    duration_sec: int = Field(alias="durationSec", gt=0)
    version: int | None = None  # Optimistic locking

    class Config:
        populate_by_name = True


class WatchProgressResponse(BaseModel):
    """시청 진행 응답"""

    content_id: int = Field(alias="contentId")
    progress_sec: int = Field(alias="progressSec")
    duration_sec: int = Field(alias="durationSec")
    completed: bool
    progress_percent: float = Field(alias="progressPercent")
    updated_at: datetime = Field(alias="updatedAt")
    version: int

    class Config:
        from_attributes = True
        populate_by_name = True


class ViewEventRequest(BaseModel):
    """시청 이벤트 요청"""

    content_id: int = Field(alias="contentId")
    event_type: Literal["play", "pause", "seek", "complete", "quality_change"] = Field(
        alias="eventType"
    )
    position_sec: int = Field(alias="positionSec", ge=0)
    metadata: dict | None = None

    class Config:
        populate_by_name = True


class HistoryItem(BaseModel):
    """시청 기록 항목"""

    content_id: int = Field(alias="contentId")
    title: str
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    duration_sec: int = Field(alias="durationSec")
    progress_sec: int = Field(alias="progressSec")
    progress_percent: float = Field(alias="progressPercent")
    completed: bool
    last_watched: datetime = Field(alias="lastWatched")

    class Config:
        populate_by_name = True


class HistoryResponse(BaseModel):
    """시청 기록 응답"""

    items: list[HistoryItem]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/watch-progress")
async def save_watch_progress(
    request: WatchProgressRequest,
    db: DbSession,
    current_user: ActiveUser,
) -> ApiResponse[WatchProgressResponse]:
    """
    시청 진행 저장

    - 🔒 인증 필요
    - Optimistic locking 지원
    """
    # Check if progress exists
    result = await db.execute(
        select(WatchProgress).where(
            and_(
                WatchProgress.user_id == current_user.id,
                WatchProgress.content_id == request.content_id,
            )
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        # Check version for optimistic locking
        if request.version is not None and progress.version != request.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "VERSION_CONFLICT",
                    "message": "다른 기기에서 업데이트되었습니다. 새로고침 후 다시 시도하세요.",
                    "currentVersion": progress.version,
                },
            )

        # Update existing
        progress.progress_sec = request.progress_sec
        progress.duration_sec = request.duration_sec
        progress.completed = request.progress_sec >= request.duration_sec * 0.95
        progress.version += 1
        progress.updated_at = datetime.now(timezone.utc)
    else:
        # Create new
        progress = WatchProgress(
            user_id=current_user.id,
            content_id=request.content_id,
            progress_sec=request.progress_sec,
            duration_sec=request.duration_sec,
            completed=request.progress_sec >= request.duration_sec * 0.95,
            version=1,
        )
        db.add(progress)

    await db.flush()
    await db.refresh(progress)

    progress_percent = (
        (progress.progress_sec / progress.duration_sec * 100)
        if progress.duration_sec > 0
        else 0
    )

    return ApiResponse(
        data=WatchProgressResponse(
            content_id=progress.content_id,
            progress_sec=progress.progress_sec,
            duration_sec=progress.duration_sec,
            completed=progress.completed,
            progress_percent=round(progress_percent, 1),
            updated_at=progress.updated_at,
            version=progress.version,
        )
    )


@router.get("/watch-progress/{content_id}")
async def get_watch_progress(
    content_id: int,
    db: DbSession,
    current_user: ActiveUser,
) -> ApiResponse[WatchProgressResponse | None]:
    """
    시청 진행 조회

    - 🔒 인증 필요
    """
    result = await db.execute(
        select(WatchProgress).where(
            and_(
                WatchProgress.user_id == current_user.id,
                WatchProgress.content_id == content_id,
            )
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        return ApiResponse(data=None)

    progress_percent = (
        (progress.progress_sec / progress.duration_sec * 100)
        if progress.duration_sec > 0
        else 0
    )

    return ApiResponse(
        data=WatchProgressResponse(
            content_id=progress.content_id,
            progress_sec=progress.progress_sec,
            duration_sec=progress.duration_sec,
            completed=progress.completed,
            progress_percent=round(progress_percent, 1),
            updated_at=progress.updated_at,
            version=progress.version,
        )
    )


@router.post("/events")
async def track_event(
    request: ViewEventRequest,
    db: DbSession,
    current_user: ActiveUser,
) -> ApiResponse[dict]:
    """
    시청 이벤트 기록

    - 🔒 인증 필요
    - 분석용 이벤트 로깅
    """
    import json

    event = ViewEvent(
        user_id=current_user.id,
        content_id=request.content_id,
        event_type=request.event_type,
        position_sec=request.position_sec,
        metadata=json.dumps(request.metadata) if request.metadata else None,
    )
    db.add(event)

    return ApiResponse(data={"recorded": True})


@router.get("/history")
async def get_history(
    db: DbSession,
    current_user: ActiveUser,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    completed: bool | None = Query(None),
) -> ApiResponse[HistoryResponse]:
    """
    시청 기록 조회

    - 🔒 인증 필요
    - 완료/미완료 필터링
    """
    query = (
        select(WatchProgress)
        .where(WatchProgress.user_id == current_user.id)
        .options(selectinload(WatchProgress.content))
    )

    if completed is not None:
        query = query.where(WatchProgress.completed == completed)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(WatchProgress.updated_at.desc())

    result = await db.execute(query)
    records = result.scalars().all()

    items = []
    for record in records:
        if record.content:
            progress_percent = (
                (record.progress_sec / record.duration_sec * 100)
                if record.duration_sec > 0
                else 0
            )
            items.append(
                HistoryItem(
                    content_id=record.content_id,
                    title=record.content.title,
                    thumbnail_url=record.content.thumbnail_url,
                    duration_sec=record.duration_sec,
                    progress_sec=record.progress_sec,
                    progress_percent=round(progress_percent, 1),
                    completed=record.completed,
                    last_watched=record.updated_at,
                )
            )

    return ApiResponse(
        data=HistoryResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
    )


@router.delete("/history/{content_id}")
async def delete_history_item(
    content_id: int,
    db: DbSession,
    current_user: ActiveUser,
) -> ApiResponse[dict]:
    """
    시청 기록 삭제

    - 🔒 인증 필요
    """
    result = await db.execute(
        select(WatchProgress).where(
            and_(
                WatchProgress.user_id == current_user.id,
                WatchProgress.content_id == content_id,
            )
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        await db.delete(progress)

    return ApiResponse(data={"deleted": True})
