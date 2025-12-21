import os
import importlib.util
import pytest

from app.core import database


@pytest.mark.asyncio
async def test_database_module_raises_when_no_env():
    original = os.environ.pop("DATABASE_URL", None)
    try:
        spec = importlib.util.spec_from_file_location("tmp_db_mod", database.__file__)
        tmp = importlib.util.module_from_spec(spec)
        with pytest.raises(ValueError) as exc:
            spec.loader.exec_module(tmp)
        assert "DATABASE_URL environment variable must be set" in str(exc.value)
    finally:
        if original is not None:
            os.environ["DATABASE_URL"] = original


@pytest.mark.asyncio
async def test_get_db_generator_executes(db_session):
    agen = database.get_db()
    async for s in agen:
        assert s is not None
        break
