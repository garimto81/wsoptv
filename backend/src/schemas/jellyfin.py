"""
Jellyfin Schemas

Jellyfin API 응답을 위한 Pydantic 스키마
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# Server Info
# =============================================================================


class JellyfinServerInfo(BaseModel):
    """Jellyfin 서버 정보"""

    server_name: str = Field(alias="ServerName")
    version: str = Field(alias="Version")
    operating_system: str | None = Field(None, alias="OperatingSystem")
    id: str = Field(alias="Id")
    startup_wizard_completed: bool = Field(True, alias="StartupWizardCompleted")

    class Config:
        populate_by_name = True


# =============================================================================
# Library / Media Folders
# =============================================================================


class JellyfinLibrary(BaseModel):
    """Jellyfin 라이브러리 (Media Folder)"""

    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    collection_type: str | None = Field(None, alias="CollectionType")
    path: str | None = Field(None, alias="Path")

    class Config:
        populate_by_name = True


class JellyfinLibraryListResponse(BaseModel):
    """라이브러리 목록 응답"""

    items: list[JellyfinLibrary] = Field(alias="Items")
    total_record_count: int = Field(alias="TotalRecordCount")

    class Config:
        populate_by_name = True


# =============================================================================
# Media Items
# =============================================================================


class JellyfinImageTags(BaseModel):
    """이미지 태그"""

    primary: str | None = Field(None, alias="Primary")
    backdrop: str | None = Field(None, alias="Backdrop")
    thumb: str | None = Field(None, alias="Thumb")

    class Config:
        populate_by_name = True


class JellyfinMediaStream(BaseModel):
    """미디어 스트림 정보 (비디오/오디오/자막)"""

    type: str = Field(alias="Type")  # Video, Audio, Subtitle
    codec: str | None = Field(None, alias="Codec")
    language: str | None = Field(None, alias="Language")
    display_title: str | None = Field(None, alias="DisplayTitle")
    index: int = Field(alias="Index")
    is_default: bool = Field(False, alias="IsDefault")
    width: int | None = Field(None, alias="Width")
    height: int | None = Field(None, alias="Height")
    bit_rate: int | None = Field(None, alias="BitRate")
    channels: int | None = Field(None, alias="Channels")
    sample_rate: int | None = Field(None, alias="SampleRate")

    class Config:
        populate_by_name = True


class JellyfinMediaSource(BaseModel):
    """미디어 소스 정보"""

    id: str = Field(alias="Id")
    name: str | None = Field(None, alias="Name")
    path: str | None = Field(None, alias="Path")
    container: str | None = Field(None, alias="Container")
    size: int | None = Field(None, alias="Size")
    bitrate: int | None = Field(None, alias="Bitrate")
    supports_direct_play: bool = Field(True, alias="SupportsDirectPlay")
    supports_direct_stream: bool = Field(True, alias="SupportsDirectStream")
    supports_transcoding: bool = Field(True, alias="SupportsTranscoding")
    media_streams: list[JellyfinMediaStream] = Field(
        default_factory=list, alias="MediaStreams"
    )

    class Config:
        populate_by_name = True


class JellyfinItem(BaseModel):
    """Jellyfin 미디어 아이템"""

    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")  # Movie, Episode, Video, Series, etc.
    overview: str | None = Field(None, alias="Overview")
    path: str | None = Field(None, alias="Path")
    parent_id: str | None = Field(None, alias="ParentId")
    series_id: str | None = Field(None, alias="SeriesId")
    series_name: str | None = Field(None, alias="SeriesName")
    index_number: int | None = Field(None, alias="IndexNumber")  # Episode number
    parent_index_number: int | None = Field(None, alias="ParentIndexNumber")  # Season
    production_year: int | None = Field(None, alias="ProductionYear")
    premiere_date: datetime | None = Field(None, alias="PremiereDate")
    date_created: datetime | None = Field(None, alias="DateCreated")
    run_time_ticks: int | None = Field(None, alias="RunTimeTicks")
    community_rating: float | None = Field(None, alias="CommunityRating")
    image_tags: JellyfinImageTags | None = Field(None, alias="ImageTags")
    media_sources: list[JellyfinMediaSource] = Field(
        default_factory=list, alias="MediaSources"
    )

    class Config:
        populate_by_name = True

    @property
    def duration_seconds(self) -> int:
        """런타임을 초 단위로 변환 (Jellyfin은 100ns 틱 단위)"""
        if self.run_time_ticks:
            return self.run_time_ticks // 10_000_000
        return 0

    @property
    def duration_minutes(self) -> int:
        """런타임을 분 단위로 변환"""
        return self.duration_seconds // 60


class JellyfinItemListResponse(BaseModel):
    """아이템 목록 응답"""

    items: list[JellyfinItem] = Field(alias="Items")
    total_record_count: int = Field(alias="TotalRecordCount")
    start_index: int = Field(0, alias="StartIndex")

    class Config:
        populate_by_name = True


# =============================================================================
# Playback
# =============================================================================


class JellyfinPlaybackInfo(BaseModel):
    """재생 정보"""

    media_sources: list[JellyfinMediaSource] = Field(
        default_factory=list, alias="MediaSources"
    )
    play_session_id: str | None = Field(None, alias="PlaySessionId")

    class Config:
        populate_by_name = True


# =============================================================================
# WSOPTV 통합용 변환 스키마
# =============================================================================


class JellyfinContentResponse(BaseModel):
    """
    Jellyfin 아이템을 WSOPTV 콘텐츠 형식으로 변환한 응답

    기존 ContentResponse와 호환되도록 필드 구성
    """

    jellyfin_id: str = Field(alias="jellyfinId")
    title: str
    description: str | None = None
    duration_sec: int = Field(alias="durationSec")
    thumbnail_url: str | None = Field(None, alias="thumbnailUrl")
    stream_url: str | None = Field(None, alias="streamUrl")
    library_name: str | None = Field(None, alias="libraryName")
    path: str | None = None
    year: int | None = None
    date_created: datetime | None = Field(None, alias="dateCreated")
    media_type: str = Field("Video", alias="mediaType")

    # HLS 스트리밍 정보
    supports_direct_play: bool = Field(True, alias="supportsDirectPlay")
    supports_hls: bool = Field(True, alias="supportsHls")

    class Config:
        populate_by_name = True

    @classmethod
    def from_jellyfin_item(
        cls,
        item: JellyfinItem,
        jellyfin_host: str,
        api_key: str,
    ) -> "JellyfinContentResponse":
        """JellyfinItem을 WSOPTV 응답 형식으로 변환"""
        # 썸네일 URL 생성
        thumbnail_url = None
        if item.image_tags and item.image_tags.primary:
            thumbnail_url = f"{jellyfin_host}/Items/{item.id}/Images/Primary"

        # HLS 스트림 URL (Direct Stream)
        stream_url = (
            f"{jellyfin_host}/Videos/{item.id}/stream.m3u8"
            f"?Static=true&mediaSourceId={item.id}&api_key={api_key}"
        )

        return cls(
            jellyfin_id=item.id,
            title=item.name,
            description=item.overview,
            duration_sec=item.duration_seconds,
            thumbnail_url=thumbnail_url,
            stream_url=stream_url,
            library_name=item.series_name,
            path=item.path,
            year=item.production_year,
            date_created=item.date_created,
            media_type=item.type,
            supports_direct_play=True,
            supports_hls=True,
        )


class JellyfinContentListResponse(BaseModel):
    """Jellyfin 콘텐츠 목록 응답 (WSOPTV 형식)"""

    items: list[JellyfinContentResponse]
    total: int
    page: int
    limit: int
    has_next: bool = Field(alias="hasNext")

    class Config:
        populate_by_name = True
