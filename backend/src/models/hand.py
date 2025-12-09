"""
Hand Model

핸드 (포커 게임 한 판) SQLAlchemy 모델
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .content import Content
    from .file import File
    from .player import Player


class Hand(Base):
    """핸드 모델"""

    __tablename__ = "hands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id: Mapped[str | None] = mapped_column(
        String(100),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
    )

    hand_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    end_sec: Mapped[int] = mapped_column(Integer, nullable=False)

    # 게임 정보
    winner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pot_size_bb: Mapped[float | None] = mapped_column(Float, nullable=True)  # Big Blind 단위
    is_all_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_showdown: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 카드 정보
    cards_shown: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    board: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "As Kh Qd 7c 2s"

    # 분류
    grade: Mapped[str] = mapped_column(
        Enum("S", "A", "B", "C", name="hand_grade"),
        default="C",
        nullable=False,
        index=True,
    )
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    highlight_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    content: Mapped["Content"] = relationship("Content", back_populates="hands")
    file: Mapped["File | None"] = relationship("File", back_populates="hands")
    players: Mapped[list["HandPlayer"]] = relationship(
        "HandPlayer",
        back_populates="hand",
        cascade="all, delete-orphan",
    )

    @property
    def duration_sec(self) -> int:
        return self.end_sec - self.start_sec

    @property
    def player_names(self) -> list[str]:
        return [hp.player.name for hp in self.players if hp.player]


class HandPlayer(Base):
    """핸드-플레이어 연결 테이블"""

    __tablename__ = "hand_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g., 'BTN', 'BB', 'UTG'
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hole_cards: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g., 'As Ah'

    # Relationships
    hand: Mapped["Hand"] = relationship("Hand", back_populates="players")
    player: Mapped["Player"] = relationship("Player", back_populates="hand_participations")
