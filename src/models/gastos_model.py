from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class Gasto(BaseModel):
    categoria: str
    nombre_gasto: str
    monto: float
    fecha: str
    descripcion: Optional[str] = None
    plan_id: Optional[UUID] = None      # ✔ IMPORTANTE
    extraordinario: Optional[bool] = False   # ✔ IMPORTANTE

class GastoUpdate(BaseModel):
    categoria: Optional[str] = None
    nombre_gasto: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[str] = None
    descripcion: Optional[str] = None
    plan_id: Optional[UUID] = None      # ✔ también en updates
    extraordinario: Optional[bool] = None
