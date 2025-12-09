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
    password: str = Field(..., min_length=4, max_length=128)
    password_confirm: str = Field(..., alias="passwordConfirm")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("영문, 숫자, 밑줄만 사용 가능합니다")
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
