from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        logger.debug("Health check: database connection OK")
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check: database connection FAILED - {str(e)}")
    
    return {
        "status": "ok",
        "version": "1.0.0",
        "database": db_status
    }