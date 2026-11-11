from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.reading import ReadingCreate, ReadingResponse, ReadingBulkCreate
from app.services import reading_service

router = APIRouter()


@router.post("/", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
async def ingest_reading(
    reading_in: ReadingCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Ingest a single reading from a dryer sensor or simulator."""
    return await reading_service.add_reading(db, reading_in)


@router.post("/bulk", response_model=List[ReadingResponse], status_code=status.HTTP_201_CREATED)
async def ingest_bulk_readings(
    bulk_in: ReadingBulkCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Ingest multiple readings."""
    results = []
    for r in bulk_in.readings:
        res = await reading_service.add_reading(db, r)
        results.append(res)
    return results

