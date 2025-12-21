from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.schemas.abastecimento import RefuelingCreate
from app.models.abastecimento import Refueling

logger = get_logger(__name__)


class RefuelingService:
    @staticmethod
    async def create_refueling(db: AsyncSession, data: RefuelingCreate) -> Refueling:
        logger.debug(f"Calculating average price for fuel type: {data.fuel_type.value}")
        
        result = await db.execute(
            select(func.avg(Refueling.price_per_liter))
            .where(Refueling.fuel_type == data.fuel_type.value)
        )
        avg_price = result.scalar()

        improper = False
        if avg_price is not None:
            avg_price_decimal = Decimal(str(avg_price))
            if data.price_per_liter > avg_price_decimal * Decimal("1.25"):
                improper = True
                logger.warning(
                    f"Anomalous price detected! Price: {data.price_per_liter}, "
                    f"Average: {avg_price_decimal}, Threshold: {avg_price_decimal * Decimal('1.25')}"
                )

        refueling = Refueling(
            station_id=data.station_id,
            timestamp=data.timestamp,
            fuel_type=data.fuel_type.value,
            price_per_liter=data.price_per_liter,
            volume_liters=data.volume_liters,
            driver_cpf=data.driver_cpf,
            improper_data=improper,
            created_at=datetime.now(timezone.utc),
        )

        db.add(refueling)
        await db.commit()
        await db.refresh(refueling)
        
        logger.debug(f"Refueling saved to database with ID: {refueling.id}")

        return refueling
