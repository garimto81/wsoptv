"""
WSOPTV Backend - FastAPI Application

포커 VOD 스트리밍 플랫폼 백엔드 서버
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import init_db

# API Routers
from .api.v1 import auth, catalogs, contents, jellyfin, search, stream, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database (create tables if not exist)
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="포커 VOD 스트리밍 플랫폼 API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "서버 오류가 발생했습니다" if not settings.DEBUG else str(exc),
            },
            "timestamp": "",
            "path": str(request.url.path),
        },
    )


# Health Check
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


# Include API Routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Auth"],
)
app.include_router(
    catalogs.router,
    prefix=f"{settings.API_V1_PREFIX}/catalogs",
    tags=["Catalogs"],
)
app.include_router(
    contents.router,
    prefix=f"{settings.API_V1_PREFIX}",
    tags=["Contents"],
)
app.include_router(
    search.router,
    prefix=f"{settings.API_V1_PREFIX}/search",
    tags=["Search"],
)
app.include_router(
    stream.router,
    prefix=f"{settings.API_V1_PREFIX}/stream",
    tags=["Stream"],
)
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"],
)
app.include_router(
    jellyfin.router,
    prefix=f"{settings.API_V1_PREFIX}/jellyfin",
    tags=["Jellyfin"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
    )
