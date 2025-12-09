"""
Player Model

포커 플레이어 SQLAlchemy 모델
"""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .hand import HandPlayer


class Player(Base):
    """플레이어 모델"""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    total_hands: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    hand_participations: Mapped[list["HandPlayer"]] = relationship(
        "HandPlayer",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    @property
    def win_rate(self) -> float:
        if self.total_hands == 0:
            return 0.0
        return (self.total_wins / self.total_hands) * 100
