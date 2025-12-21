from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal
from typing import List
    
from app.utils.enums import FuelType
from app.utils.validators import validate_volume_positive
import re


class RefuelingCreate(BaseModel):
    station_id: int
    timestamp: datetime
    fuel_type: FuelType
    price_per_liter: Decimal
    volume_liters: Decimal
    driver_cpf: str

    @field_validator('driver_cpf')
    @classmethod
    def validate_driver_cpf(cls, v: str) -> str:
        # Clean formatting and keep digits only. Do not raise here; service
        # layer will decide if CPF is invalid for business rules.
        cpf_clean = re.sub(r'[^0-9]', '', v)
        return cpf_clean
    
    @field_validator('price_per_liter')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Preço por litro deve ser maior que zero')
        return v
    
    @field_validator('volume_liters')
    @classmethod
    def validate_volume(cls, v: Decimal) -> Decimal:
        # Delegate volume > 0 validation to shared validator so it occurs
        # at schema parsing time (earlier in the flow), consistent with
        # other validations located in `app/utils/validators.py`.
        return validate_volume_positive(v)


class RefuelingResponse(RefuelingCreate):
    id: int
    improper_data: bool
    created_at: datetime

    class Config:
        from_attributes = True
