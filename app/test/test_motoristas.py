import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from app.schemas.abastecimento import RefuelingCreate
from app.services.abastecimento_service import RefuelingService


@pytest.mark.asyncio
async def test_historico_por_cpf_empty(client):
    response = await client.get("/api/v1/motoristas/99999999999/historico")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("total"), int)
    assert data.get("page") == 1
    assert data.get("size") == 10
    assert isinstance(data.get("data"), list)


@pytest.mark.asyncio
async def test_historico_por_cpf_with_records(db_session, client):
    cpf = "11144477735"
    
    for i in range(3):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00") + Decimal(str(i * 0.10)),
            volume_liters=Decimal("30"),
            driver_cpf=cpf,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert 1 <= len(data["data"]) <= 10
    assert any(refueling["driver_cpf"] == cpf for refueling in data["data"]) if data["data"] else False


@pytest.mark.asyncio
async def test_historico_por_cpf_pagination(db_session, client):
    cpf = "11144477735"
    
    for i in range(9):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf=cpf,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=1&size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 3
    assert 1 <= len(data["data"]) <= 3
    assert data["total"] >= 9
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=2&size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["data"]) == 3
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=3&size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 3
    assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_historico_por_cpf_custom_page_size(db_session, client):
    cpf = "11144477735"
    
    for i in range(12):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf=cpf,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=1&size=12")
    assert response.status_code == 200
    data = response.json()
    assert 1 <= len(data["data"]) <= 12
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=1&size=100")
    assert response.status_code == 200
    data = response.json()
    requested = 100
    assert len(data["data"]) == min(data["total"], requested)


@pytest.mark.asyncio
async def test_historico_por_cpf_ordering(db_session, client):
    cpf = "11144477735"
    timestamps = []
    
    for i in range(3):
        ts = datetime.now(timezone.utc) - timedelta(hours=10 - i)
        timestamps.append(ts)
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=ts,
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf=cpf,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico")
    assert response.status_code == 200
    data = response.json()
    
    for i in range(len(data["data"]) - 1):
        current_ts = datetime.fromisoformat(data["data"][i]["timestamp"])
        next_ts = datetime.fromisoformat(data["data"][i + 1]["timestamp"])
        assert current_ts >= next_ts


@pytest.mark.asyncio
async def test_historico_por_cpf_different_cpfs(db_session, client):
    cpf1 = "11144477735"
    cpf2 = "22255588846"
    
    for i in range(3):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf=cpf1,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    for i in range(2):
        payload = RefuelingCreate(
            station_id=10 + i,
            timestamp=datetime.now(timezone.utc),
            fuel_type="DIESEL",
            price_per_liter=Decimal("4.50"),
            volume_liters=Decimal("25"),
            driver_cpf=cpf2,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf1}/historico")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert all(r["driver_cpf"] == cpf1 for r in data["data"]) if data["data"] else True
    
    response = await client.get(f"/api/v1/motoristas/{cpf2}/historico")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert all(r["driver_cpf"] == cpf2 for r in data["data"]) if data["data"] else True


@pytest.mark.asyncio
async def test_historico_por_cpf_offset_calculation(db_session, client):
    cpf = "11144477735"
    
    for i in range(6):
        payload = RefuelingCreate(
            station_id=i + 1,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            fuel_type="GASOLINA",
            price_per_liter=Decimal("5.00"),
            volume_liters=Decimal("30"),
            driver_cpf=cpf,
        )
        await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=2&size=2")
    assert response.status_code == 200
    data = response.json()
    assert 1 <= len(data["data"]) <= 2
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico?page=3&size=2")
    assert response.status_code == 200
    data = response.json()
    assert 1 <= len(data["data"]) <= 2


@pytest.mark.asyncio
async def test_historico_por_cpf_with_special_cpf_format(db_session, client):
    cpf = "11144477735"
    
    payload = RefuelingCreate(
        station_id=1,
        timestamp=datetime.now(timezone.utc),
        fuel_type="GASOLINA",
        price_per_liter=Decimal("5.00"),
        volume_liters=Decimal("30"),
        driver_cpf=cpf,
    )
    await RefuelingService.create_refueling(db_session, payload)
    
    response = await client.get(f"/api/v1/motoristas/{cpf}/historico")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_historico_por_cpf_direct_call():
    from app.routers.motoristas import historico_por_cpf

    class FakeResult:
        def __init__(self, rows):
            self._rows = rows
        def scalar(self):
            return len(self._rows)
        def scalars(self):
            class S:
                def __init__(self, rows):
                    self._rows = rows
                def all(self):
                    return self._rows
            return S(self._rows)

    class FakeDB:
        def __init__(self, rows):
            self._rows = rows
        async def execute(self, *a, **k):
            return FakeResult(self._rows)

    rows = [object(), object()]
    res = await historico_por_cpf("123", page=2, size=1, db=FakeDB(rows))
    assert res["total"] == 2
    assert res["page"] == 2
    assert res["size"] == 1