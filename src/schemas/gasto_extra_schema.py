from pydantic import BaseModel
from datetime import date
from typing import Optional

class GastoExtraCreate(BaseModel):
    plan_id: int                 # id del plan al que se aplica
    monto: float
    nombre_gasto: Optional[str] = None
    fecha: date
    descripcion: Optional[str] = None