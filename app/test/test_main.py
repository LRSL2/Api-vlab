import pytest

from app.main import startup_event, shutdown_event


@pytest.mark.asyncio
async def test_startup_event_executes():
    await startup_event()


@pytest.mark.asyncio
async def test_shutdown_event_executes():
    await shutdown_event()


@pytest.mark.asyncio
async def test_startup_and_shutdown_sequence():
    await startup_event()
    await shutdown_event()
