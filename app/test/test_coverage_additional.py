import os
import importlib.util
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException

from app.main import app, startup_event, shutdown_event
from app.core import database
from app.core.security import get_api_key
from app.core.database import get_db
from app.services.abastecimento_service import RefuelingService
from app.models.abastecimento import Refueling
from app.schemas.abastecimento import RefuelingCreate
from app.utils.enums import FuelType
from decimal import Decimal
from datetime import datetime, timezone, date


@pytest.mark.asyncio
async def test_get_api_key_accepts_and_rejects():
    os.environ["API_KEY"] = "test-accept-key"
    key = await get_api_key("test-accept-key")
    assert key == "test-accept-key"

    with pytest.raises(HTTPException) as exc:
        await get_api_key("wrong-key")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_health_db_error_shows_error():
    async def fake_get_db():
        class FakeSession:
            async def execute(self, *a, **k):
                raise RuntimeError("db failure simulated")
        yield FakeSession()

    app.dependency_overrides[get_db] = fake_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 200
    jr = resp.json()
    assert jr["database"].startswith("error:")


@pytest.mark.asyncio
async def test_database_module_raises_when_no_env():
    original = os.environ.pop("DATABASE_URL", None)
    try:
        spec = importlib.util.spec_from_file_location("tmp_db_mod", database.__file__)
        tmp = importlib.util.module_from_spec(spec)
        with pytest.raises(ValueError):
            spec.loader.exec_module(tmp)
    finally:
        if original is not None:
            os.environ["DATABASE_URL"] = original


@pytest.mark.asyncio
async def test_get_db_generator_executes(db_session):
    agen = database.get_db()
    async for s in agen:
        assert s is not None
        break


@pytest.mark.asyncio
async def test_create_refueling_handles_service_value_error(client, monkeypatch):
    async def raise_value_error(db, ref):
        raise ValueError("forced error")

    monkeypatch.setattr(RefuelingService, "create_refueling", raise_value_error)

    payload = {
        "station_id": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.50",
        "volume_liters": "10.0",
        "driver_cpf": "12345678901"
    }

    resp = await client.post("/api/v1/abastecimentos", json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert "forced error" in data["detail"]


@pytest.mark.asyncio
async def test_list_refuelings_filters_and_pagination(client, db_session):
    now = datetime.now(timezone.utc)
    items = []
    for i in range(5):
        items.append(Refueling(
            station_id=i,
            timestamp=now,
            fuel_type=FuelType.GASOLINA.value,
            price_per_liter=Decimal("4.0"),
            volume_liters=Decimal("10.0"),
            driver_cpf="11111111111",
            improper_data=False
        ))
    for i in range(3):
        items.append(Refueling(
            station_id=100 + i,
            timestamp=now,
            fuel_type=FuelType.DIESEL.value,
            price_per_liter=Decimal("3.0"),
            volume_liters=Decimal("5.0"),
            driver_cpf="22222222222",
            improper_data=False
        ))

    db_session.add_all(items)
    await db_session.commit()

    resp = await client.get("/api/v1/abastecimentos", params={"fuel_type": "GASOLINA"})
    assert resp.status_code == 200
    jr = resp.json()
    assert jr["total"] >= 5

    resp2 = await client.get("/api/v1/abastecimentos", params={"refueling_date": date.today().isoformat()})
    assert resp2.status_code == 200
    jr2 = resp2.json()
    assert "data" in jr2


@pytest.mark.asyncio
async def test_main_startup_and_shutdown():
    await startup_event()
    await shutdown_event()


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


@pytest.mark.asyncio
async def test_list_refuelings_direct_call_branches():
    from app.api.v1.abastecimento import list_refuelings

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

    rows = [object() for _ in range(3)]
    res = await list_refuelings(fuel_type=None, refueling_date=None, page=1, size=10, db=FakeDB(rows))
    assert res["total"] == 3

    res2 = await list_refuelings(fuel_type=FuelType.GASOLINA, refueling_date=None, page=1, size=10, db=FakeDB(rows))
    assert res2["total"] == 3

    some_date = date.today()
    res3 = await list_refuelings(fuel_type=None, refueling_date=some_date, page=1, size=10, db=FakeDB(rows))
    assert res3["total"] == 3


@pytest.mark.asyncio
async def test_health_direct_branches():
    from app.routers.health import health

    class GoodDB:
        async def execute(self, *a, **k):
            return None

    class BadDB:
        async def execute(self, *a, **k):
            raise RuntimeError("boom")

    ok = await health(db=GoodDB())
    assert ok["database"] == "connected"

    bad = await health(db=BadDB())
    assert bad["database"].startswith("error:")


@pytest.mark.asyncio
async def test_create_refueling_success_logs(client):
    payload = {
        "station_id": 2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fuel_type": "GASOLINA",
        "price_per_liter": "5.50",
        "volume_liters": "30.0",
        "driver_cpf": "11122233344"
    }

    response = await client.post("/api/v1/abastecimentos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert "improper_data" in data


@pytest.mark.asyncio
async def test_create_refueling_direct_with_logger(db_session):
    from app.api.v1.abastecimento import create_refueling
    
    class DummyRef:
        id = 999
        improper_data = False
    
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
