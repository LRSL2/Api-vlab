import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.services.abastecimento_service import RefuelingService
from app.schemas.abastecimento import RefuelingCreate
from app.models.abastecimento import Refueling

@pytest.mark.asyncio
async def test_improper_data_when_price_above_25_percent(db_session):
    base = Refueling(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("30"),
        driver_cpf="123",
        improper_data=False,
    )
    db_session.add(base)
    await db_session.commit()

    payload = RefuelingCreate(
        station_id=2,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=base.price_per_liter * Decimal("1.26"),
        volume_liters=Decimal("20"),
        driver_cpf="12345678910",
    )

    result = await RefuelingService.create_refueling(db_session, payload)

    assert result.improper_data is True

@pytest.mark.asyncio
async def test_negative_volume_raises_error(db_session):
    with pytest.raises(ValueError):
        RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="ETANOL",
            price_per_liter=Decimal("3.50"),
            volume_liters=Decimal("-10"),
            driver_cpf="123",
        )
