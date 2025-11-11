from pydantic import BaseModel, Field
from datetime import date

class Periodo(BaseModel):
    inicio: date
    fin: date

class ReporteRangoResp(BaseModel):
    periodo: Periodo
    total_ingresos: float = Field(0, ge=0)
    total_gastos: float = Field(0, ge=0)
    total_ahorro: float = Field(0, ge=0)
    balance: float
