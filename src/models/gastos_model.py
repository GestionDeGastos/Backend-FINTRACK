from pydantic import BaseModel
from typing import Optional

class Gasto(BaseModel):
    categoria: str
    nombre_gasto: str
    monto: float
    fecha: str
    descripcion: Optional[str] = None

class GastoUpdate(BaseModel):
    categoria: Optional[str] = None
    nombre_gasto: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[str] = None
    descripcion: Optional[str] = None