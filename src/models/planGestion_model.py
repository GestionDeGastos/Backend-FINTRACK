from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class PlanGestion(BaseModel):
    """Modelo completo de plan de gestión"""
    id: Optional[int] = None
    usuario_id: Optional[str] = None  # Se obtiene del token
    nombre_plan: str
    ingreso_total: float
    ahorro_deseado: Optional[float] = None
    duracion_meses: int
    distribucion_gastos: Optional[Dict[str, float]] = None  # Se genera automáticamente
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlanGestionCreate(BaseModel):
    """Modelo para crear un plan (lo que envía el frontend)"""
    nombre_plan: str
    ingreso_total: float
    ahorro_deseado: Optional[float] = None
    duracion_meses: int

    class Config:
        schema_extra = {
            "example": {
                "nombre_plan": "Plan Vacaciones 2025",
                "ingreso_total": 5000,
                "ahorro_deseado": 1000,
                "duracion_meses": 12
            }
        }


class PlanGestionUpdate(BaseModel):
    """Modelo para actualizar un plan"""
    nombre_plan: Optional[str] = None
    ingreso_total: Optional[float] = None
    ahorro_deseado: Optional[float] = None
    duracion_meses: Optional[int] = None