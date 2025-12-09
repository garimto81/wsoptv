"""
Catalog Model

카탈로그 (WSOP, HCL, PAD 등) SQLAlchemy 모델
"""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .series import Series


class Catalog(Base):
    """카탈로그 모델"""

    __tablename__ = "catalogs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 'wsop', 'hcl', 'pad'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    series: Mapped[list["Series"]] = relationship(
        "Series",
        back_populates="catalog",
        cascade="all, delete-orphan",
        order_by="desc(Series.year)",
    )

    @property
    def series_count(self) -> int:
        return len(self.series)
