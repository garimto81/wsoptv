"""
Application Configuration

환경 변수 기반 설정 관리
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "WSOPTV"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "wsoptv"
    POSTGRES_PASSWORD: str = "wsoptv_password"
    POSTGRES_DB: str = "wsoptv"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # MeiliSearch
    MEILI_HOST: str = "http://localhost:7700"
    MEILI_MASTER_KEY: str = "masterKey"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    BCRYPT_ROUNDS: int = 12

    # NAS / Streaming
    NAS_MOUNT_PATH: str = "/mnt/nas"
    NAS_UNC_PREFIX: str = "\\\\10.10.100.122\\docker\\GGPNAs"  # DB에 저장된 UNC 경로 prefix
    HLS_SEGMENT_DURATION: int = 6
    HLS_CACHE_PATH: str = "/tmp/hls-cache"

    def convert_nas_path(self, db_path: str) -> str:
        """
        DB에 저장된 NAS 경로를 컨테이너 내부 경로로 변환

        예: \\\\10.10.100.122\\docker\\GGPNAs/ARCHIVE/MPP/...
         -> /mnt/nas/GGPNAs/ARCHIVE/MPP/...
        """
        if not db_path:
            return db_path

        # UNC prefix 제거 및 Linux 경로로 변환
        path = db_path.replace("\\", "/")

        # 여러 형태의 UNC prefix 처리
        prefixes = [
            "//10.10.100.122/docker/GGPNAs",
            "//10.10.100.122/docker",
        ]

        for prefix in prefixes:
            if path.startswith(prefix):
                relative_path = path[len(prefix):]
                return f"{self.NAS_MOUNT_PATH}/GGPNAs{relative_path}"

        # 변환 불가시 원본 반환 (로컬 경로일 수 있음)
        return db_path

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Jellyfin
    JELLYFIN_HOST: str = "http://localhost:8096"  # Backend → Jellyfin (Docker 내부 통신)
    JELLYFIN_BROWSER_HOST: str = ""  # Browser → Jellyfin (비어있으면 JELLYFIN_HOST 사용)
    JELLYFIN_API_KEY: str = ""

    @property
    def JELLYFIN_PUBLIC_HOST(self) -> str:
        """브라우저에서 접근 가능한 Jellyfin 호스트 URL"""
        return self.JELLYFIN_BROWSER_HOST or self.JELLYFIN_HOST

    @property
    def JELLYFIN_AUTH_HEADER(self) -> str:
        """Jellyfin 10.11+ Authorization header format"""
        return f'MediaBrowser Token="{self.JELLYFIN_API_KEY}", Client="WSOPTV", Device="Backend", DeviceId="wsoptv-backend-001", Version="1.0.0"'


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
