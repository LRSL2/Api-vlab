import pytest
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from app.api.v1.abastecimento import router
from app.schemas.abastecimento import RefuelingCreate
from app.services.abastecimento_service import RefuelingService
from app.core.security import get_api_key
from app.core.database import get_db
from app.utils.validators import validate_cpf, validate_volume_positive
from app.routers.health import router as health_router
from app.routers.motoristas import router as motoristas_router


@pytest.mark.asyncio
async def test_create_refueling_with_validation_error(client, db_session):
    with pytest.raises(ValidationError):
        RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("0"),  
            driver_cpf="11144477735",
        )


def test_validate_cpf_with_all_zeros():
    with pytest.raises(ValueError, match="CPF inválido"):
        validate_cpf("00000000000")


def test_validate_cpf_with_too_few_digits():
    with pytest.raises(ValueError, match="CPF deve conter 11 dígitos"):
        validate_cpf("123456789")


def test_validate_cpf_with_invalid_check_digit_first():
    with pytest.raises(ValueError, match="CPF inválido"):
        validate_cpf("11144477700")


def test_validate_cpf_with_invalid_check_digit_second():
    with pytest.raises(ValueError, match="CPF inválido"):
        validate_cpf("11144477700")


def test_validate_volume_positive_zero():
    with pytest.raises(ValueError, match="Volume deve ser maior que zero"):
        validate_volume_positive(Decimal("0"))


def test_validate_volume_positive_negative():
    with pytest.raises(ValueError, match="Volume deve ser maior que zero"):
        validate_volume_positive(Decimal("-5.5"))


def test_validate_volume_positive_valid():
    result = validate_volume_positive(Decimal("10.5"))
    assert result == Decimal("10.5")


def test_refueling_create_with_zero_price():
    with pytest.raises(ValidationError):
        RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("0"),
            volume_liters=Decimal("10"),
            driver_cpf="11144477735",
        )


def test_refueling_create_with_negative_price():
    with pytest.raises(ValidationError):
        RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("-5.00"), 
            volume_liters=Decimal("10"),
            driver_cpf="11144477735",
        )


def test_refueling_cpf_with_formatting_cleaned():
    refueling = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("10"),
        driver_cpf="111.444.777-35",
    )
    assert refueling.driver_cpf == "11144477735"


@pytest.mark.asyncio
async def test_create_refueling_with_diesel(db_session):
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="DIESEL",
        price_per_liter=Decimal("4.50"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    result = await RefuelingService.create_refueling(db_session, payload)
    assert result.fuel_type == "DIESEL"


@pytest.mark.asyncio
async def test_create_refueling_with_etanol(db_session):
    payload = RefuelingCreate(
        station_id=2,
        timestamp=datetime.now(timezone.utc),
        fuel_type="ETANOL",
        price_per_liter=Decimal("3.50"),
        volume_liters=Decimal("25"),
        driver_cpf="11144477735",
    )
    result = await RefuelingService.create_refueling(db_session, payload)
    assert result.fuel_type == "ETANOL"


@pytest.mark.asyncio
async def test_list_refuelings_with_date_filter(client, db_session):
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    
    payload_today = {
        "station_id": 1,
        "timestamp": today.isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.00",
        "volume_liters": "40",
        "driver_cpf": "11144477735"
    }
    response = await client.post("/api/v1/abastecimentos", json=payload_today, headers={"X-API-Key": "test-key"})
    assert response.status_code == 201
    
    response = await client.get(f"/api/v1/abastecimentos?refueling_date={today.date()}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_refueling_create_missing_required_field():
    with pytest.raises(ValidationError):
        RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            # Missing price_per_liter
            volume_liters=Decimal("10"),
            driver_cpf="11144477735",
        )


@pytest.mark.asyncio
async def test_get_refuelings_without_security_check(client):
    response = await client.get("/api/v1/abastecimentos")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_multiple_refuelings_same_station(db_session):
    for i in range(5):
        payload = RefuelingCreate(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00") + Decimal(str(i * 0.10)),
            volume_liters=Decimal("30"),
            driver_cpf="11144477735",
        )
        result = await RefuelingService.create_refueling(db_session, payload)
        assert result.station_id == 1


@pytest.mark.asyncio
async def test_create_refueling_price_at_exactly_25_percent(db_session):
    base = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("4.00"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    base_result = await RefuelingService.create_refueling(db_session, base)
    assert base_result.improper_data is False
    
    at_threshold = RefuelingCreate(
        station_id=2,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),  
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    threshold_result = await RefuelingService.create_refueling(db_session, at_threshold)
    assert threshold_result.improper_data is False


def test_cpf_validator_with_another_valid_cpf():
    result = validate_cpf("11144477735")
    assert result == "11144477735"


def test_validate_cpf_with_non_numeric():
    result = validate_cpf("111-444-777-35")
    assert len(result) == 11





@pytest.mark.asyncio
async def test_health_check_response(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_refuelings_with_specific_date_filtering(client, db_session):
    today = datetime.now(timezone.utc)
    
    payload_today = RefuelingCreate(
        station_id=1,
        timestamp=today,
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("40"),
        driver_cpf="11144477735"
    )
    await RefuelingService.create_refueling(db_session, payload_today)
    
    other_day = today - timedelta(days=10)
    payload_other = RefuelingCreate(
        station_id=2,
        timestamp=other_day,
        fuel_type="DIESEL",
        price_per_liter=Decimal("4.50"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735"
    )
    await RefuelingService.create_refueling(db_session, payload_other)
    
    response = await client.get(f"/api/v1/abastecimentos?refueling_date={today.date()}")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_list_refuelings_combined_filters(client, db_session):
    today = datetime.now(timezone.utc)
    
    payload = RefuelingCreate(
        station_id=1,
        timestamp=today,
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("40"),
        driver_cpf="11144477735"
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/abastecimentos?fuel_type=GASOLINA&refueling_date={today.date()}")
    assert response.status_code == 200
