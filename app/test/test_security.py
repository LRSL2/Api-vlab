import os
import pytest
from fastapi import HTTPException

from app.core.security import get_api_key


@pytest.mark.asyncio
async def test_get_api_key_accepts_valid_key():
    os.environ["API_KEY"] = "test-accept-key"
    key = await get_api_key("test-accept-key")
    assert key == "test-accept-key"


@pytest.mark.asyncio
async def test_get_api_key_rejects_invalid_key():
    os.environ["API_KEY"] = "valid-key"
    with pytest.raises(HTTPException) as exc:
        await get_api_key("wrong-key")
    assert exc.value.status_code == 403
    assert "Invalid or missing API Key" in exc.value.detail


@pytest.mark.asyncio
async def test_get_api_key_rejects_none():
    with pytest.raises(HTTPException) as exc:
        await get_api_key(None)
    assert exc.value.status_code == 403
