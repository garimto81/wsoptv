"""
File Model

미디어 파일 메타데이터 SQLAlchemy 모델
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .content import Content
    from .hand import Hand


class File(Base):
    """미디어 파일 모델"""

    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # hash or uuid
    nas_path: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)

    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g., '1920x1080'
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., 'h264'
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    bitrate_kbps: Mapped[int | None] = mapped_column(Integer, nullable=True)

    hls_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hls_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    contents: Mapped[list["Content"]] = relationship(
        "Content",
        back_populates="file",
    )
    hands: Mapped[list["Hand"]] = relationship(
        "Hand",
        back_populates="file",
    )
