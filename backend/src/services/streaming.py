"""
Streaming Service

HLS 스트리밍 및 트랜스코딩 서비스
"""

import asyncio
import hashlib
import os
from pathlib import Path
from typing import AsyncGenerator

from ..core.config import settings


class StreamingService:
    """HLS 스트리밍 서비스"""

    def __init__(self):
        self.cache_path = Path(settings.HLS_CACHE_PATH)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.segment_duration = settings.HLS_SEGMENT_DURATION

    def get_content_cache_path(self, content_id: int, quality: str = "720p") -> Path:
        """콘텐츠별 캐시 경로"""
        return self.cache_path / f"{content_id}" / quality

    def get_manifest_path(self, content_id: int, quality: str = "720p") -> Path:
        """HLS 매니페스트 파일 경로"""
        return self.get_content_cache_path(content_id, quality) / "manifest.m3u8"

    def get_segment_path(
        self, content_id: int, segment_index: int, quality: str = "720p"
    ) -> Path:
        """HLS 세그먼트 파일 경로"""
        return self.get_content_cache_path(content_id, quality) / f"segment_{segment_index:05d}.ts"

    async def generate_master_manifest(
        self,
        content_id: int,
        duration_sec: int,
        available_qualities: list[str] | None = None,
    ) -> str:
        """
        마스터 HLS 매니페스트 생성

        Args:
            content_id: 콘텐츠 ID
            duration_sec: 총 길이 (초)
            available_qualities: 사용 가능한 품질 목록

        Returns:
            M3U8 매니페스트 문자열
        """
        qualities = available_qualities or ["360p", "480p", "720p", "1080p"]

        # Quality to bandwidth mapping
        quality_config = {
            "360p": {"bandwidth": 800000, "resolution": "640x360"},
            "480p": {"bandwidth": 1400000, "resolution": "854x480"},
            "720p": {"bandwidth": 2800000, "resolution": "1280x720"},
            "1080p": {"bandwidth": 5000000, "resolution": "1920x1080"},
        }

        lines = [
            "#EXTM3U",
            "#EXT-X-VERSION:3",
        ]

        for quality in qualities:
            config = quality_config.get(quality, quality_config["720p"])
            lines.extend([
                f'#EXT-X-STREAM-INF:BANDWIDTH={config["bandwidth"]},RESOLUTION={config["resolution"]}',
                f"playlist_{quality}.m3u8",
            ])

        return "\n".join(lines)

    async def generate_quality_manifest(
        self,
        content_id: int,
        duration_sec: int,
        quality: str = "720p",
    ) -> str:
        """
        품질별 HLS 매니페스트 생성

        Args:
            content_id: 콘텐츠 ID
            duration_sec: 총 길이 (초)
            quality: 품질

        Returns:
            M3U8 매니페스트 문자열
        """
        num_segments = (duration_sec + self.segment_duration - 1) // self.segment_duration

        lines = [
            "#EXTM3U",
            "#EXT-X-VERSION:3",
            f"#EXT-X-TARGETDURATION:{self.segment_duration}",
            "#EXT-X-MEDIA-SEQUENCE:0",
            "#EXT-X-PLAYLIST-TYPE:VOD",
        ]

        for i in range(num_segments):
            # Calculate actual segment duration (last segment may be shorter)
            if i == num_segments - 1:
                seg_duration = duration_sec - (i * self.segment_duration)
            else:
                seg_duration = self.segment_duration

            lines.extend([
                f"#EXTINF:{seg_duration:.3f},",
                f"segment_{i:05d}.ts",
            ])

        lines.append("#EXT-X-ENDLIST")

        return "\n".join(lines)

    async def get_segment(
        self,
        content_id: int,
        segment_index: int,
        nas_path: str,
        quality: str = "720p",
    ) -> AsyncGenerator[bytes, None]:
        """
        HLS 세그먼트 스트리밍 (On-demand 트랜스먹싱)

        Args:
            content_id: 콘텐츠 ID
            segment_index: 세그먼트 인덱스
            nas_path: NAS 파일 경로
            quality: 품질

        Yields:
            세그먼트 바이트 청크
        """
        segment_path = self.get_segment_path(content_id, segment_index, quality)

        # Check cache first
        if segment_path.exists():
            async for chunk in self._read_file_chunks(segment_path):
                yield chunk
            return

        # Generate segment on-demand
        segment_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = segment_index * self.segment_duration

        # Quality settings
        quality_settings = {
            "360p": "-vf scale=640:360 -b:v 800k -maxrate 856k -bufsize 1200k",
            "480p": "-vf scale=854:480 -b:v 1400k -maxrate 1498k -bufsize 2100k",
            "720p": "-vf scale=1280:720 -b:v 2800k -maxrate 2996k -bufsize 4200k",
            "1080p": "-vf scale=1920:1080 -b:v 5000k -maxrate 5350k -bufsize 7500k",
        }

        video_settings = quality_settings.get(quality, quality_settings["720p"])

        # FFmpeg command for HLS segment
        ffmpeg_cmd = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", nas_path,
            "-t", str(self.segment_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            *video_settings.split(),
            "-c:a", "aac",
            "-b:a", "128k",
            "-f", "mpegts",
            "-y",
            str(segment_path),
        ]

        # Run FFmpeg
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.wait()

        # Stream the generated segment
        if segment_path.exists():
            async for chunk in self._read_file_chunks(segment_path):
                yield chunk

    async def _read_file_chunks(
        self, file_path: Path, chunk_size: int = 65536
    ) -> AsyncGenerator[bytes, None]:
        """파일을 청크 단위로 읽기"""
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def get_cache_key(self, content_id: int, quality: str, segment: int) -> str:
        """Redis 캐시 키 생성"""
        return f"hls:{content_id}:{quality}:seg:{segment}"

    async def clear_cache(self, content_id: int) -> None:
        """콘텐츠 캐시 삭제"""
        cache_dir = self.cache_path / str(content_id)
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)


# Singleton instance
streaming_service = StreamingService()
