from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.models.abastecimento import Refueling
from app.schemas.abastecimento import RefuelingResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])
logger = get_logger(__name__)

@router.get("/{cpf}/historico", response_model=PaginatedResponse[RefuelingResponse])
async def historico_por_cpf(
    cpf: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Fetching refueling history for CPF: {cpf}, page: {page}, size: {size}")
    offset = (page - 1) * size

    count_query = select(func.count(Refueling.id)).where(Refueling.driver_cpf == cpf)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    data_query = (
        select(Refueling)
        .where(Refueling.driver_cpf == cpf)
        .order_by(desc(Refueling.timestamp))
        .offset(offset)
        .limit(size)
    )

    result = await db.execute(data_query)
    data = result.scalars().all()
    
    logger.info(f"Found {total} total refuelings for CPF {cpf}, returning {len(data)} for current page")

    return {
        "total": total,
        "page": page,
        "size": size,
        "data": data
    }
