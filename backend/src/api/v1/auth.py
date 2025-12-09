"""
Auth API Router

인증 관련 API 엔드포인트
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from sqlalchemy import select

from ...core.config import settings
from ...core.database import get_db
from ...core.deps import ActiveUser, CurrentUser, DbSession
from ...core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ...models.user import User, UserSession
from ...schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenRefreshResponse,
    UserResponse,
)
from ...schemas.common import ApiResponse

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: DbSession,
) -> ApiResponse[RegisterResponse]:
    """
    회원가입 (pending 상태로 생성)

    - 아이디 중복 체크
    - 비밀번호 규칙 검증
    - 관리자 승인 후 로그인 가능
    """
    # Validate password confirmation
    if not request.validate_passwords_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "AUTH_PASSWORD_MISMATCH",
                "message": "비밀번호가 일치하지 않습니다",
            },
        )

    # Check username exists
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "AUTH_USERNAME_EXISTS",
                "message": "이미 존재하는 아이디입니다",
            },
        )

    # Create user
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        display_name=request.display_name or request.username,
        status="pending",
        role="user",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return ApiResponse(
        data=RegisterResponse(
            user=UserResponse.model_validate(user),
            message="가입이 완료되었습니다. 관리자 승인을 기다려주세요.",
        )
    )


@router.post("/login")
async def login(
    request: LoginRequest,
    response: Response,
    db: DbSession,
) -> ApiResponse[AuthResponse]:
    """
    로그인 - httpOnly 쿠키 기반

    - Access Token: 15분 (쿠키로 전달)
    - Refresh Token: 7일 (쿠키로 전달)
    """
    # Find user
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_INVALID_CREDENTIALS",
                "message": "아이디 또는 비밀번호가 잘못되었습니다",
            },
        )

    # Check user status
    if user.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AUTH_PENDING_APPROVAL",
                "message": "관리자 승인을 기다리는 중입니다",
            },
        )
    if user.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AUTH_REJECTED",
                "message": "가입이 거절되었습니다",
            },
        )
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "AUTH_SUSPENDED",
                "message": "계정이 정지되었습니다",
            },
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires,
    )

    # Save session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires,
    )
    db.add(session)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=f"{settings.API_V1_PREFIX}/auth",
    )

    expires_at = datetime.now(timezone.utc) + access_token_expires

    return ApiResponse(
        data=AuthResponse(
            user=UserResponse.model_validate(user),
            expires_at=expires_at,
        )
    )


@router.post("/refresh")
async def refresh_token(
    response: Response,
    db: DbSession,
    refresh_token: str | None = Cookie(None),
) -> ApiResponse[TokenRefreshResponse]:
    """
    Access Token 갱신

    - Refresh Token (쿠키)으로 새 Access Token 발급
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_MISSING",
                "message": "인증 토큰이 없습니다",
            },
        )

    # Decode refresh token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_INVALID",
                "message": "유효하지 않은 토큰입니다",
            },
        )

    # Find session
    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.revoked_at.is_(None),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_REVOKED",
                "message": "토큰이 무효화되었습니다",
            },
        )

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_EXPIRED",
                "message": "토큰이 만료되었습니다",
            },
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(session.user_id)},
        expires_delta=access_token_expires,
    )

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    expires_at = datetime.now(timezone.utc) + access_token_expires

    return ApiResponse(
        data=TokenRefreshResponse(expires_at=expires_at)
    )


@router.post("/logout")
async def logout(
    response: Response,
    db: DbSession,
    current_user: CurrentUser,
    refresh_token: str | None = Cookie(None),
) -> ApiResponse[dict[str, str]]:
    """
    로그아웃 - 토큰 무효화

    - Refresh Token 세션 삭제
    - 쿠키 삭제
    """
    # Revoke session if refresh token exists
    if refresh_token:
        result = await db.execute(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.revoked_at.is_(None),
            )
        )
        session = result.scalar_one_or_none()
        if session:
            session.revoked_at = datetime.now(timezone.utc)

    # Delete cookies
    response.delete_cookie(
        key="access_token",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        path=f"{settings.API_V1_PREFIX}/auth",
    )

    return ApiResponse(data={"message": "로그아웃되었습니다"})


@router.get("/me")
async def get_me(
    current_user: ActiveUser,
) -> ApiResponse[UserResponse]:
    """
    현재 사용자 정보

    - 🔒 인증 필요 (approved 상태)
    """
    return ApiResponse(data=UserResponse.model_validate(current_user))
