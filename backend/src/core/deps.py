"""
Dependencies

FastAPI dependency injection
"""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .security import decode_token
from ..models.user import User


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """
    Get current authenticated user from httpOnly cookie

    Raises:
        HTTPException: 401 if not authenticated or token invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 필요합니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise credentials_exception

    payload = decode_token(access_token)
    if payload is None:
        raise credentials_exception

    # Check token type
    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active (approved) user

    Raises:
        HTTPException: 403 if user is not approved
    """
    if current_user.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 승인을 기다리는 중입니다",
        )
    if current_user.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가입이 거절되었습니다",
        )
    if current_user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="계정이 정지되었습니다",
        )

    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current admin user

    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )

    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
