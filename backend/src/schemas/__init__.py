# Pydantic Schemas
from .auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    TokenRefreshResponse,
)
from .catalog import CatalogResponse, CatalogListResponse, CatalogDetailResponse
from .series import SeriesResponse, SeriesDetailResponse
from .content import ContentResponse, ContentDetailResponse, ContentListResponse
from .hand import HandResponse, HandListResponse
from .player import PlayerResponse, PlayerListResponse
from .search import SearchRequest, SearchResponse, SuggestResponse
from .common import PaginatedResponse, ApiResponse, ErrorResponse
from .jellyfin import (
    JellyfinServerInfo,
    JellyfinLibrary,
    JellyfinItem,
    JellyfinItemListResponse,
    JellyfinPlaybackInfo,
    JellyfinContentResponse,
    JellyfinContentListResponse,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "AuthResponse",
    "TokenRefreshResponse",
    # Catalog
    "CatalogResponse",
    "CatalogListResponse",
    "CatalogDetailResponse",
    # Series
    "SeriesResponse",
    "SeriesDetailResponse",
    # Content
    "ContentResponse",
    "ContentDetailResponse",
    "ContentListResponse",
    # Hand
    "HandResponse",
    "HandListResponse",
    # Player
    "PlayerResponse",
    "PlayerListResponse",
    # Search
    "SearchRequest",
    "SearchResponse",
    "SuggestResponse",
    # Common
    "PaginatedResponse",
    "ApiResponse",
    "ErrorResponse",
    # Jellyfin
    "JellyfinServerInfo",
    "JellyfinLibrary",
    "JellyfinItem",
    "JellyfinItemListResponse",
    "JellyfinPlaybackInfo",
    "JellyfinContentResponse",
    "JellyfinContentListResponse",
]
