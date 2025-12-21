from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Query

from app.schemas.abastecimento import RefuelingCreate, RefuelingResponse
from app.services.abastecimento_service import RefuelingService
from app.core.database import get_db
from app.models.abastecimento import Refueling

router = APIRouter(prefix="/abastecimentos", tags=["Abastecimentos"])


@router.get(
    "/",
    response_model=list[RefuelingResponse]
)
async def list_refuelings(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * size

    result = await db.execute(
        select(Refueling)
        .offset(offset)
        .limit(size)
    )

    refuelings = result.scalars().all()
    return refuelings


@router.post(
    "/",
    response_model=RefuelingResponse,
    status_code=201
)
async def create_refueling(
    payload: RefuelingCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        refueling = await RefuelingService.create_refueling(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return refueling
