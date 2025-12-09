"""
User Models

사용자 관련 SQLAlchemy 모델
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .content import Content


class User(Base):
    """사용자 모델"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    role: Mapped[str] = mapped_column(
        Enum("user", "admin", name="user_role"),
        default="user",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", "suspended", name="user_status"),
        default="pending",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    view_events: Mapped[list["ViewEvent"]] = relationship(
        "ViewEvent",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSession(Base):
    """사용자 세션 모델"""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    device_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")


class WatchProgress(Base):
    """시청 진행 상태 모델"""

    __tablename__ = "watch_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    progress_sec: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Optimistic locking

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="watch_progress")
    content: Mapped["Content"] = relationship("Content", back_populates="watch_progress")

    __table_args__ = (
        # Unique constraint per user+content
        {"sqlite_autoincrement": True},
    )


class ViewEvent(Base):
    """시청 이벤트 로그 모델"""

    __tablename__ = "view_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        Enum("play", "pause", "seek", "complete", "quality_change", name="event_type"),
        nullable=False,
    )
    position_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    event_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="view_events")
    content: Mapped["Content"] = relationship("Content", back_populates="view_events")
