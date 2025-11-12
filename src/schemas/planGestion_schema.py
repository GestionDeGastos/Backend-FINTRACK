from pydantic import BaseModel, Field, field_validator
from typing import Optional

class PlanGestionSchema(BaseModel):
    """Schema para validar datos de entrada del plan"""
    nombre_plan: str = Field(..., min_length=1, max_length=255, description="Nombre del plan")
    ingreso_total: float = Field(..., gt=0, description="Ingreso total mensual")
    ahorro_deseado: Optional[float] = Field(None, ge=0, description="Monto deseado para ahorrar")
    duracion_meses: int = Field(..., gt=0, le=360, description="Duración del plan en meses (máx 30 años)")

    @field_validator('ahorro_deseado')
    @classmethod
    def ahorro_no_puede_exceder_ingreso(cls, v, info):
        if v is not None and info.data.get('ingreso_total') and v > info.data.get('ingreso_total'):
            raise ValueError('El ahorro no puede ser mayor que el ingreso total')
        return v

    class Config:
        schema_extra = {
            "example": {
                "nombre_plan": "Plan Vacaciones 2025",
                "ingreso_total": 5000,
                "ahorro_deseado": 1000,
                "duracion_meses": 12
            }
        }