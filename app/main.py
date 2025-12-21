from fastapi import FastAPI

from app.core.logging_config import setup_logging, get_logger
from app.routers.health import router as health_router
from app.routers.motoristas import router as motoristas_router
from app.api.v1.abastecimento import router as abastecimento_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Vlab API",
    description="API de Gateway para Data Lake de Abastecimento",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Vlab API...")
    logger.info("API version: 1.0.0")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Vlab API...")

app.include_router(abastecimento_router, prefix="/api/v1")
app.include_router(motoristas_router, prefix="/api/v1")
app.include_router(health_router)