"""
Content Model

콘텐츠 (에피소드) SQLAlchemy 모델
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .series import Series
    from .file import File
    from .hand import Hand
    from .user import WatchProgress, ViewEvent


class Content(Base):
    """콘텐츠 모델"""

    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    series_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    episode_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_sec: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    series: Mapped["Series"] = relationship("Series", back_populates="contents")
    file: Mapped["File | None"] = relationship("File", back_populates="contents")
    hands: Mapped[list["Hand"]] = relationship(
        "Hand",
        back_populates="content",
        cascade="all, delete-orphan",
        order_by="Hand.start_sec",
    )
    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress",
        back_populates="content",
        cascade="all, delete-orphan",
    )
    view_events: Mapped[list["ViewEvent"]] = relationship(
        "ViewEvent",
        back_populates="content",
        cascade="all, delete-orphan",
    )

    @property
    def hands_count(self) -> int:
        return len(self.hands)
