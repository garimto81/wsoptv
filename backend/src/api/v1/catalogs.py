"""
Catalogs API Router

카탈로그 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ...core.deps import ActiveUser, DbSession
from ...models.catalog import Catalog
from ...models.content import Content
from ...models.series import Series
from ...schemas.catalog import (
    CatalogDetailResponse,
    CatalogListResponse,
    CatalogResponse,
    SeriesSummary,
)
from ...schemas.common import ApiResponse

router = APIRouter()


@router.get("")
async def list_catalogs(
    db: DbSession,
    _: ActiveUser,  # 인증 필요
) -> ApiResponse[CatalogListResponse]:
    """
    카탈로그 목록

    - 🔒 인증 필요
    """
    # Get catalogs with series count
    result = await db.execute(
        select(Catalog)
        .options(selectinload(Catalog.series).selectinload(Series.contents))
        .order_by(Catalog.sort_order)
    )
    catalogs = result.scalars().all()

    items = []
    for catalog in catalogs:
        content_count = sum(len(s.contents) for s in catalog.series)
        items.append(
            CatalogResponse(
                id=catalog.id,
                name=catalog.name,
                display_title=catalog.display_title,
                description=catalog.description,
                thumbnail_url=catalog.thumbnail_url,
                series_count=len(catalog.series),
                content_count=content_count,
            )
        )

    return ApiResponse(
        data=CatalogListResponse(
            items=items,
            total=len(items),
        )
    )


@router.get("/{catalog_id}")
async def get_catalog(
    catalog_id: str,
    db: DbSession,
    _: ActiveUser,  # 인증 필요
) -> ApiResponse[CatalogDetailResponse]:
    """
    카탈로그 상세

    - 🔒 인증 필요
    - 시리즈 목록 포함
    """
    result = await db.execute(
        select(Catalog)
        .where(Catalog.id == catalog_id)
        .options(selectinload(Catalog.series).selectinload(Series.contents))
    )
    catalog = result.scalar_one_or_none()

    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CATALOG_NOT_FOUND",
                "message": "카탈로그를 찾을 수 없습니다",
            },
        )

    series_list = [
        SeriesSummary(
            id=s.id,
            title=s.title,
            year=s.year,
            episode_count=len(s.contents),
            thumbnail_url=s.thumbnail_url,
        )
        for s in catalog.series
    ]

    return ApiResponse(
        data=CatalogDetailResponse(
            id=catalog.id,
            name=catalog.name,
            display_title=catalog.display_title,
            description=catalog.description,
            thumbnail_url=catalog.thumbnail_url,
            series=series_list,
        )
    )
