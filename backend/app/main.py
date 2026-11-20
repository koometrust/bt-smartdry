from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.v1.router import api_router
from app.services.ml_service import get_ml_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize embedded ML models
    ml_service = get_ml_service()
    ml_service.load_models()
    yield
    # Shutdown: Halt background simulator if active
    from app.services.simulator_service import simulator_manager
    if simulator_manager.is_running:
        await simulator_manager.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    ml_service = get_ml_service()
    if not ml_service.is_loaded:
        ml_service.load_models()

    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    is_healthy = db_status == "connected" and ml_service.is_loaded
    return {
        "status": "healthy" if is_healthy else "degraded",
        "database": db_status,
        "ml_models_loaded": ml_service.is_loaded,
        "sms_provider_mode": settings.SMS_PROVIDER_MODE,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

