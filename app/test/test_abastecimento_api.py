import pytest
from decimal import Decimal
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_create_refueling_direct_call(db_session):
    from app.api.v1.abastecimento import create_refueling
    from app.schemas.abastecimento import RefuelingCreate
    
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("10.0"),
        driver_cpf="11122233344",
    )
    
    result = await create_refueling(payload, db=db_session, api_key="test-key")
    assert result.id > 0
    assert hasattr(result, "improper_data")
