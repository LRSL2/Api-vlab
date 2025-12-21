from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Refueling(Base):
    __tablename__ = "refuelings"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    fuel_type = Column(String, nullable=False, index=True)
    price_per_liter = Column(Numeric(10, 2), nullable=False)
    volume_liters = Column(Numeric(10, 2), nullable=False)
    driver_cpf = Column(String, nullable=False, index=True)
    improper_data = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_fuel_type_timestamp', 'fuel_type', 'timestamp'),
    )