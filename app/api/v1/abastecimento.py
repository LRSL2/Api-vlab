from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, time
from typing import Optional

from app.core.database import get_db
from app.core.security import get_api_key
from app.core.logging_config import get_logger
from app.models.abastecimento import Refueling
from app.schemas.abastecimento import RefuelingCreate, RefuelingResponse
from app.schemas.pagination import PaginatedResponse
from app.services.abastecimento_service import RefuelingService
from app.utils.enums import FuelType

router = APIRouter(tags=["Refuelings"])
logger = get_logger(__name__)

@router.post(
    "/abastecimentos",
    response_model=RefuelingResponse,
    status_code=201
)
async def create_refueling(
    refueling: RefuelingCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    try:
        logger.info(f"Creating refueling for station {refueling.station_id}, driver CPF: {refueling.driver_cpf}")
        created = await RefuelingService.create_refueling(db, refueling)
        logger.info(f"Refueling created successfully with ID: {created.id}, improper_data: {created.improper_data}")
        return created
    except ValueError as e:
        logger.error(f"Validation error creating refueling: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/abastecimentos",
    response_model=PaginatedResponse[RefuelingResponse]
)
async def list_refuelings(
    fuel_type: Optional[FuelType] = Query(None, description="Tipo de combustível"),
    refueling_date: Optional[date] = Query(None, description="Data do abastecimento"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Listing refuelings - page: {page}, size: {size}, fuel_type: {fuel_type}, date: {refueling_date}")
    offset = (page - 1) * size

    base_query = select(Refueling)
    count_query = select(func.count(Refueling.id))

    if fuel_type:
        base_query = base_query.where(Refueling.fuel_type == fuel_type.value)
        count_query = count_query.where(Refueling.fuel_type == fuel_type.value)

    if refueling_date:
        start = datetime.combine(refueling_date, time.min)
        end = datetime.combine(refueling_date, time.max)
        base_query = base_query.where(Refueling.timestamp.between(start, end))
        count_query = count_query.where(Refueling.timestamp.between(start, end))

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    data_query = (
        base_query
        .order_by(desc(Refueling.timestamp))
        .offset(offset)
        .limit(size)
    )

    result = await db.execute(data_query)
    data = result.scalars().all()
    
    logger.info(f"Found {total} total refuelings, returning {len(data)} for current page")
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": data
    }