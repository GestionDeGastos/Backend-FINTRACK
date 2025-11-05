from pydantic import BaseModel
from typing import Optional

class Ingreso(BaseModel):
    concepto: str
    nombre_fuente: str
    monto: float
    fecha: str
    descripcion: Optional[str] = None

class IngresoUpdate(BaseModel):
    concepto: Optional[str] = None
    nombre_fuente: Optional[str] = None
    monto: Optional[float] = None
    fecha: Optional[str] = None
    descripcion: Optional[str] = None