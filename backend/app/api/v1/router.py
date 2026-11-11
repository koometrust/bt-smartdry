from fastapi import APIRouter

from app.api.v1.endpoints import auth, hubs, batches, readings, alerts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(hubs.router, prefix="/hubs", tags=["Hubs"])
api_router.include_router(batches.router, prefix="/batches", tags=["Batches"])
api_router.include_router(readings.router, prefix="/readings", tags=["Readings"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

