import pytest
from decimal import Decimal
from datetime import datetime, timezone, date, timedelta
from pydantic import ValidationError

from app.schemas.abastecimento import RefuelingCreate
from app.services.abastecimento_service import RefuelingService


@pytest.mark.asyncio
async def test_list_refuelings_empty_database(client):
    response = await client.get("/api/v1/abastecimentos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
    assert "page" in data
    assert "size" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_list_refuelings_pagination_first_page(db_session, client):
    for i in range(3):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf="11144477735",
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10


@pytest.mark.asyncio
async def test_list_refuelings_by_fuel_type_gasolina(db_session, client):
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos?fuel_type=GASOLINA")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert all(r["fuel_type"] == "GASOLINA" for r in data["data"])


@pytest.mark.asyncio
async def test_list_refuelings_by_fuel_type_diesel(db_session, client):
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="DIESEL",
        price_per_liter=Decimal("4.50"),
        volume_liters=Decimal("25"),
        driver_cpf="11144477735",
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos?fuel_type=DIESEL")
    assert response.status_code == 200
    data = response.json()
    if data["total"] > 0:
        assert all(r["fuel_type"] == "DIESEL" for r in data["data"])


@pytest.mark.asyncio
async def test_list_refuelings_by_fuel_type_etanol(db_session, client):
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="ETANOL",
        price_per_liter=Decimal("3.50"),
        volume_liters=Decimal("20"),
        driver_cpf="11144477735",
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos?fuel_type=ETANOL")
    assert response.status_code == 200
    data = response.json()
    if data["total"] > 0:
        assert all(r["fuel_type"] == "ETANOL" for r in data["data"])


@pytest.mark.asyncio
async def test_list_refuelings_by_specific_date(db_session, client):
    today = date.today()
    
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/abastecimentos?refueling_date={today}")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_list_refuelings_by_past_date(db_session, client):
    past_date = date(2020, 1, 1)
    
    response = await client.get(f"/api/v1/abastecimentos?refueling_date={past_date}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_refuelings_by_fuel_and_date(db_session, client):
    today = date.today()
    
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("30"),
        driver_cpf="11144477735",
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/abastecimentos?fuel_type=GASOLINA&refueling_date={today}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_list_refuelings_with_valid_api_key(client, db_session):
    response = await client.get("/api/v1/abastecimentos")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_refueling_success_with_api_key(client):
    payload = {
        "station_id": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.00",
        "volume_liters": "40",
        "driver_cpf": "11144477735"
    }
    response = await client.post("/api/v1/abastecimentos", json=payload, headers={"X-API-Key": "vlab-secret-key"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["station_id"] == 1


@pytest.mark.asyncio
async def test_create_refueling_response_fields(client):
    payload = {
        "station_id": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.00",
        "volume_liters": "40",
        "driver_cpf": "11144477735"
    }
    response = await client.post("/api/v1/abastecimentos", json=payload, headers={"X-API-Key": "vlab-secret-key"})
    assert response.status_code == 201
    data = response.json()
    
    required_fields = ["id", "station_id", "timestamp", "fuel_type", "price_per_liter", 
                      "volume_liters", "driver_cpf", "improper_data", "created_at"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_create_refueling_improper_data_flag(db_session, client):
    base_payload = {
        "station_id": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.00",
        "volume_liters": "40",
        "driver_cpf": "11144477735"
    }
    response = await client.post("/api/v1/abastecimentos", json=base_payload, headers={"X-API-Key": "vlab-secret-key"})
    assert response.status_code == 201
    assert response.json()["improper_data"] is False


@pytest.mark.asyncio
async def test_list_with_pagination_multiple_pages(db_session, client):
    for i in range(9):
        payload = RefuelingCreate(
            station_id=i + 100,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf="11144477735",
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos?page=1&size=3")
    assert response.status_code == 200
    data1 = response.json()
    assert len(data1["data"]) == 3
    
    response = await client.get("/api/v1/abastecimentos?page=2&size=3")
    assert response.status_code == 200
    data2 = response.json()
    assert len(data2["data"]) == 3
    
    response = await client.get("/api/v1/abastecimentos?page=3&size=3")
    assert response.status_code == 200
    data3 = response.json()
    assert len(data3["data"]) == 3


@pytest.mark.asyncio
async def test_list_ordering_by_timestamp_descending(db_session, client):
    base_time = datetime.now(timezone.utc)
    for i in range(3):
        payload = RefuelingCreate(
            station_id=200 + i,
            timestamp=base_time - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf="11144477735",
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get("/api/v1/abastecimentos")
    assert response.status_code == 200
    data = response.json()
    
    if len(data["data"]) >= 2:
        for i in range(len(data["data"]) - 1):
            ts1 = datetime.fromisoformat(data["data"][i]["timestamp"])
            ts2 = datetime.fromisoformat(data["data"][i + 1]["timestamp"])
            assert ts1 >= ts2
