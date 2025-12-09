"""
Search Service

MeiliSearch 통합 검색 서비스
"""

from typing import Any

import meilisearch
from meilisearch.errors import MeilisearchError

from ..core.config import settings


class SearchService:
    """MeiliSearch 검색 서비스"""

    def __init__(self):
        self.client = meilisearch.Client(
            settings.MEILI_HOST,
            settings.MEILI_MASTER_KEY,
        )
        self._indexes = {
            "contents": "wsoptv_contents",
            "players": "wsoptv_players",
            "hands": "wsoptv_hands",
        }

    async def search(
        self,
        query: str,
        index_name: str = "contents",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "relevance",
    ) -> dict[str, Any]:
        """
        통합 검색

        Args:
            query: 검색어
            index_name: 인덱스 이름 (contents, players, hands)
            filters: 필터 조건
            page: 페이지 번호
            limit: 결과 개수
            sort: 정렬 방식 (relevance, date, views)

        Returns:
            검색 결과
        """
        try:
            index = self.client.index(self._indexes[index_name])

            # Build filter string
            filter_str = self._build_filter(filters) if filters else None

            # Build sort
            sort_list = self._build_sort(sort)

            # Search options
            options: dict[str, Any] = {
                "offset": (page - 1) * limit,
                "limit": limit,
                "attributesToHighlight": ["title", "description"],
                "facets": ["catalog_id", "player_names", "grade", "year"],
            }

            if filter_str:
                options["filter"] = filter_str

            if sort_list:
                options["sort"] = sort_list

            result = index.search(query, options)

            return {
                "results": result["hits"],
                "total": result.get("estimatedTotalHits", 0),
                "page": page,
                "limit": limit,
                "facets": result.get("facetDistribution", {}),
                "processing_time_ms": result.get("processingTimeMs", 0),
            }

        except MeilisearchError as e:
            # Return empty results on error (graceful degradation)
            return {
                "results": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "facets": {},
                "error": str(e),
            }

    async def suggest(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        자동완성 제안

        Args:
            query: 검색어
            limit: 최대 결과 수

        Returns:
            제안 목록
        """
        suggestions = []

        try:
            # Search contents
            contents_index = self.client.index(self._indexes["contents"])
            contents_result = contents_index.search(
                query,
                {"limit": limit // 2, "attributesToRetrieve": ["id", "title"]},
            )
            for hit in contents_result["hits"]:
                suggestions.append({
                    "text": hit["title"],
                    "type": "content",
                    "id": hit["id"],
                })

            # Search players
            players_index = self.client.index(self._indexes["players"])
            players_result = players_index.search(
                query,
                {"limit": limit // 2, "attributesToRetrieve": ["id", "name", "display_name"]},
            )
            for hit in players_result["hits"]:
                suggestions.append({
                    "text": hit.get("display_name", hit["name"]),
                    "type": "player",
                    "id": hit["id"],
                })

        except MeilisearchError:
            pass  # Return partial results

        return suggestions[:limit]

    def _build_filter(self, filters: dict[str, Any]) -> str | None:
        """필터 문자열 생성"""
        conditions = []

        if filters.get("catalog_id"):
            conditions.append(f'catalog_id = "{filters["catalog_id"]}"')

        if filters.get("player_id"):
            conditions.append(f"player_ids = {filters['player_id']}")

        if filters.get("hand_grade"):
            conditions.append(f'grade = "{filters["hand_grade"]}"')

        if filters.get("year"):
            conditions.append(f"year = {filters['year']}")

        return " AND ".join(conditions) if conditions else None

    def _build_sort(self, sort: str) -> list[str] | None:
        """정렬 조건 생성"""
        sort_map = {
            "date": ["created_at:desc"],
            "views": ["view_count:desc"],
            "relevance": None,  # MeiliSearch default
        }
        return sort_map.get(sort)

    async def index_content(self, content: dict[str, Any]) -> None:
        """콘텐츠 인덱싱"""
        try:
            index = self.client.index(self._indexes["contents"])
            index.add_documents([content])
        except MeilisearchError:
            pass

    async def index_player(self, player: dict[str, Any]) -> None:
        """플레이어 인덱싱"""
        try:
            index = self.client.index(self._indexes["players"])
            index.add_documents([player])
        except MeilisearchError:
            pass

    async def create_indexes(self) -> None:
        """인덱스 생성 및 설정"""
        try:
            # Contents index
            contents_index = self.client.index(self._indexes["contents"])
            contents_index.update_settings({
                "searchableAttributes": [
                    "title",
                    "description",
                    "player_names",
                ],
                "filterableAttributes": [
                    "catalog_id",
                    "player_ids",
                    "grade",
                    "year",
                ],
                "sortableAttributes": [
                    "created_at",
                    "view_count",
                ],
                "displayedAttributes": [
                    "id",
                    "title",
                    "description",
                    "thumbnail_url",
                    "duration_sec",
                    "view_count",
                    "catalog_id",
                    "series_title",
                    "hands_count",
                ],
            })

            # Players index
            players_index = self.client.index(self._indexes["players"])
            players_index.update_settings({
                "searchableAttributes": [
                    "name",
                    "display_name",
                ],
                "sortableAttributes": [
                    "total_hands",
                    "total_wins",
                ],
            })

        except MeilisearchError:
            pass


# Singleton instance
search_service = SearchService()
