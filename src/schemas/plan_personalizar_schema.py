from pydantic import BaseModel
from typing import Dict

class PlanPersonalizarSchema(BaseModel):
    """
    Schema para recibir los nuevos porcentajes personalizados.
    El usuario envía algo como:
    {
        "porcentajes": {
            "alimentación": 30,
            "vivienda": 25,
            "transporte": 20,
            "entretenimiento": 15,
            "otros": 10
        }
    }
    """
    porcentajes: Dict[str, float]
