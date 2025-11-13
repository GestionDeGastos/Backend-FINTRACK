from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PlanGestionCreate(BaseModel):
    categoria: str = Field(..., description="Categoría del plan de gestión de gasto")
    monto_limite: float = Field(..., gt=0, description="Monto máximo permitido")
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str] = None

class PlanGestionResp(BaseModel):
    id: int
    categoria: str
    monto_limite: float
    fecha_inicio: date
    fecha_fin: date
    descripcion: Optional[str] = None
    usuario_id: str
