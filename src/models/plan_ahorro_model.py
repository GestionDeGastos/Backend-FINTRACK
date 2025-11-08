from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PlanAhorro(BaseModel):
    nombre_plan: str = Field(..., min_length=1, max_length=255, description="Nombre del plan de ahorro")
    monto_objetivo: float = Field(..., gt=0, description="Monto objetivo a ahorrar (debe ser mayor a 0)")
    fecha_inicio: str = Field(..., description="Fecha de inicio (formato: YYYY-MM-DD)")
    fecha_fin: str = Field(..., description="Fecha de fin (formato: YYYY-MM-DD)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional del plan")

class PlanAhorroUpdate(BaseModel):
    nombre_plan: Optional[str] = Field(None, min_length=1, max_length=255)
    monto_objetivo: Optional[float] = Field(None, gt=0)
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    descripcion: Optional[str] = Field(None, max_length=500)

class PlanAhorroResponse(BaseModel):
    id: str
    usuario_id: str
    nombre_plan: str
    monto_objetivo: float
    fecha_inicio: str
    fecha_fin: str
    descripcion: Optional[str]
    creado_en: str
    actualizado_en: str