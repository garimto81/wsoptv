"""
Migration Service

pokervod.db (SQLite) → PostgreSQL 마이그레이션
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings


class MigrationService:
    """SQLite → PostgreSQL 마이그레이션 서비스"""

    def __init__(self, sqlite_path: str = "D:/AI/claude01/shared-data/pokervod.db"):
        self.sqlite_path = Path(sqlite_path)

    def connect_sqlite(self) -> sqlite3.Connection:
        """SQLite 연결"""
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")

        conn = sqlite3.connect(str(self.sqlite_path))
        conn.row_factory = sqlite3.Row
        return conn

    async def migrate_all(self, db: AsyncSession) -> dict[str, int]:
        """전체 마이그레이션 실행"""
        results = {}

        conn = self.connect_sqlite()
        try:
            results["catalogs"] = await self.migrate_catalogs(db, conn)
            results["series"] = await self.migrate_series(db, conn)
            results["files"] = await self.migrate_files(db, conn)
            results["contents"] = await self.migrate_contents(db, conn)
            results["players"] = await self.migrate_players(db, conn)
            results["hands"] = await self.migrate_hands(db, conn)
            results["hand_players"] = await self.migrate_hand_players(db, conn)

            await db.commit()

        finally:
            conn.close()

        return results

    async def migrate_catalogs(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """카탈로그 마이그레이션"""
        cursor = conn.execute("SELECT DISTINCT catalog_id FROM series")
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            catalog_id = row["catalog_id"]
            if not catalog_id:
                continue

            # Map catalog names
            catalog_map = {
                "wsop": ("WSOP", "World Series of Poker"),
                "hcl": ("HCL", "Hustler Casino Live"),
                "pad": ("PAD", "Poker After Dark"),
                "ggmillions": ("GGMillions", "GG Millions"),
            }

            name, display_title = catalog_map.get(
                catalog_id.lower(),
                (catalog_id.upper(), catalog_id)
            )

            await db.execute(
                text("""
                    INSERT INTO catalogs (id, name, display_title, sort_order)
                    VALUES (:id, :name, :display_title, :sort_order)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": catalog_id.lower(),
                    "name": name,
                    "display_title": display_title,
                    "sort_order": count,
                },
            )
            count += 1

        return count

    async def migrate_series(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """시리즈 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, catalog_id, title, year, season_num, description
            FROM series
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            await db.execute(
                text("""
                    INSERT INTO series (id, catalog_id, title, year, season_num, description)
                    VALUES (:id, :catalog_id, :title, :year, :season_num, :description)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        year = EXCLUDED.year
                """),
                {
                    "id": row["id"],
                    "catalog_id": row["catalog_id"].lower() if row["catalog_id"] else "unknown",
                    "title": row["title"] or f"Series {row['id']}",
                    "year": row["year"] or 2020,
                    "season_num": row["season_num"],
                    "description": row["description"],
                },
            )
            count += 1

        return count

    async def migrate_files(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """파일 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, nas_path, filename, size_bytes, duration_sec,
                   resolution, codec, fps, bitrate_kbps
            FROM files
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            file_id = row["id"] or hashlib.md5(row["nas_path"].encode()).hexdigest()[:16]

            await db.execute(
                text("""
                    INSERT INTO files (id, nas_path, filename, size_bytes, duration_sec,
                                       resolution, codec, fps, bitrate_kbps)
                    VALUES (:id, :nas_path, :filename, :size_bytes, :duration_sec,
                            :resolution, :codec, :fps, :bitrate_kbps)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": file_id,
                    "nas_path": row["nas_path"],
                    "filename": row["filename"] or Path(row["nas_path"]).name,
                    "size_bytes": row["size_bytes"] or 0,
                    "duration_sec": row["duration_sec"] or 0,
                    "resolution": row["resolution"],
                    "codec": row["codec"],
                    "fps": row["fps"],
                    "bitrate_kbps": row["bitrate_kbps"],
                },
            )
            count += 1

        return count

    async def migrate_contents(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """콘텐츠 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, series_id, file_id, episode_num, title,
                   description, duration_sec, view_count
            FROM contents
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            await db.execute(
                text("""
                    INSERT INTO contents (id, series_id, file_id, episode_num, title,
                                          description, duration_sec, view_count)
                    VALUES (:id, :series_id, :file_id, :episode_num, :title,
                            :description, :duration_sec, :view_count)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        duration_sec = EXCLUDED.duration_sec
                """),
                {
                    "id": row["id"],
                    "series_id": row["series_id"],
                    "file_id": row["file_id"],
                    "episode_num": row["episode_num"],
                    "title": row["title"] or f"Content {row['id']}",
                    "description": row["description"],
                    "duration_sec": row["duration_sec"] or 0,
                    "view_count": row["view_count"] or 0,
                },
            )
            count += 1

        return count

    async def migrate_players(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """플레이어 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, name, display_name, country, total_hands, total_wins
            FROM players
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            await db.execute(
                text("""
                    INSERT INTO players (id, name, display_name, country, total_hands, total_wins)
                    VALUES (:id, :name, :display_name, :country, :total_hands, :total_wins)
                    ON CONFLICT (id) DO UPDATE SET
                        display_name = EXCLUDED.display_name,
                        total_hands = EXCLUDED.total_hands,
                        total_wins = EXCLUDED.total_wins
                """),
                {
                    "id": row["id"],
                    "name": row["name"],
                    "display_name": row["display_name"] or row["name"],
                    "country": row["country"],
                    "total_hands": row["total_hands"] or 0,
                    "total_wins": row["total_wins"] or 0,
                },
            )
            count += 1

        return count

    async def migrate_hands(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """핸드 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, content_id, file_id, hand_number, start_sec, end_sec,
                   winner, pot_size_bb, is_all_in, is_showdown,
                   cards_shown, board, grade, tags, highlight_score
            FROM hands
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            grade = row["grade"] if row["grade"] in ("S", "A", "B", "C") else "C"

            await db.execute(
                text("""
                    INSERT INTO hands (id, content_id, file_id, hand_number, start_sec, end_sec,
                                       winner, pot_size_bb, is_all_in, is_showdown,
                                       cards_shown, board, grade, tags, highlight_score)
                    VALUES (:id, :content_id, :file_id, :hand_number, :start_sec, :end_sec,
                            :winner, :pot_size_bb, :is_all_in, :is_showdown,
                            :cards_shown, :board, :grade, :tags, :highlight_score)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": row["id"],
                    "content_id": row["content_id"],
                    "file_id": row["file_id"],
                    "hand_number": row["hand_number"],
                    "start_sec": row["start_sec"] or 0,
                    "end_sec": row["end_sec"] or 0,
                    "winner": row["winner"],
                    "pot_size_bb": row["pot_size_bb"],
                    "is_all_in": bool(row["is_all_in"]),
                    "is_showdown": bool(row["is_showdown"]),
                    "cards_shown": row["cards_shown"],
                    "board": row["board"],
                    "grade": grade,
                    "tags": row["tags"],
                    "highlight_score": row["highlight_score"] or 0,
                },
            )
            count += 1

        return count

    async def migrate_hand_players(
        self, db: AsyncSession, conn: sqlite3.Connection
    ) -> int:
        """핸드-플레이어 연결 마이그레이션"""
        cursor = conn.execute("""
            SELECT id, hand_id, player_id, position, is_winner, hole_cards
            FROM hand_players
        """)
        rows = cursor.fetchall()

        count = 0
        for row in rows:
            await db.execute(
                text("""
                    INSERT INTO hand_players (id, hand_id, player_id, position, is_winner, hole_cards)
                    VALUES (:id, :hand_id, :player_id, :position, :is_winner, :hole_cards)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": row["id"],
                    "hand_id": row["hand_id"],
                    "player_id": row["player_id"],
                    "position": row["position"],
                    "is_winner": bool(row["is_winner"]),
                    "hole_cards": row["hole_cards"],
                },
            )
            count += 1

        return count


# Singleton
migration_service = MigrationService()
