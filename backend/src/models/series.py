"""
Series Model

시리즈 SQLAlchemy 모델
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .catalog import Catalog
    from .content import Content


class Series(Base):
    """시리즈 모델"""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    catalog_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("catalogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    season_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    catalog: Mapped["Catalog"] = relationship("Catalog", back_populates="series")
    contents: Mapped[list["Content"]] = relationship(
        "Content",
        back_populates="series",
        cascade="all, delete-orphan",
        order_by="Content.episode_num",
    )

    @property
    def episode_count(self) -> int:
        return len(self.contents)

    @property
    def content_count(self) -> int:
        return len(self.contents)
