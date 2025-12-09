"""
Auth Schemas

인증 관련 Pydantic 스키마
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """회원가입 요청"""

    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., alias="passwordConfirm")
    display_name: str | None = Field(None, min_length=2, max_length=100, alias="displayName")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("영문, 숫자, 밑줄만 사용 가능합니다")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("대문자를 포함해야 합니다")
        if not re.search(r"[a-z]", v):
            raise ValueError("소문자를 포함해야 합니다")
        if not re.search(r"[0-9]", v):
            raise ValueError("숫자를 포함해야 합니다")

        weak_passwords = ["password", "12345678", "qwerty"]
        if any(p in v.lower() for p in weak_passwords):
            raise ValueError("너무 쉬운 비밀번호입니다")

        return v

    def validate_passwords_match(self) -> bool:
        return self.password == self.password_confirm

    class Config:
        populate_by_name = True


class LoginRequest(BaseModel):
    """로그인 요청"""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """사용자 응답"""

    id: int
    username: str
    display_name: str | None = Field(None, alias="displayName")
    avatar_url: str | None = Field(None, alias="avatarUrl")
    role: str
    status: str
    created_at: datetime = Field(alias="createdAt")
    last_login_at: datetime | None = Field(None, alias="lastLoginAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class AuthResponse(BaseModel):
    """인증 응답 (로그인 성공)"""

    user: UserResponse
    expires_at: datetime = Field(alias="expiresAt")

    class Config:
        populate_by_name = True


class TokenRefreshResponse(BaseModel):
    """토큰 갱신 응답"""

    expires_at: datetime = Field(alias="expiresAt")

    class Config:
        populate_by_name = True


class RegisterResponse(BaseModel):
    """회원가입 응답"""

    user: UserResponse
    message: str
