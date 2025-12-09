"""
Common Schemas

공통 응답 형식
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """API 성공 응답"""

    data: T
    meta: dict[str, Any] | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답"""

    items: list[T]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True


class ErrorDetail(BaseModel):
    """에러 상세"""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """API 에러 응답"""

    error: ErrorDetail
    timestamp: datetime
    path: str
