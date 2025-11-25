from datetime import datetime
from typing import Dict, Any

def generar_plan(ingreso_total: float, ahorro_deseado: float, duracion_meses: int) -> Dict[str, Any]:
    """
    Genera un plan financiero automático basado en el ingreso, ahorro y duración del usuario.

    Parámetros:
        ingreso_total (float): ingreso mensual total del usuario.
        ahorro_deseado (float): cantidad mensual que el usuario desea ahorrar.
        duracion_meses (int): duración del plan en meses.

    Retorna:
        dict: Un diccionario con la siguiente estructura:
            {
                "nombre_plan": str,
                "ingreso_total": float,
                "ahorro_deseado": float,
                "duracion_meses": int,
                "fecha_creacion": str,
                "distribucion_gastos": Dict[str, float],
                "totales": {
                    "total_ingresos": float,
                    "total_gastos": float,
                    "total_ahorro": float,
                    "balance_final": float
                }
            }
    """

    # Validaciones más completas
    if ingreso_total <= 0:
        return {"error": "El ingreso total debe ser mayor a 0"}
    
    if duracion_meses <= 0:
        return {"error": "La duración en meses debe ser mayor a 0"}
    
    if ahorro_deseado < 0:
        return {"error": "El ahorro deseado no puede ser negativo"}
    
    if ahorro_deseado > ingreso_total:
        return {"error": "El ahorro deseado no puede ser mayor al ingreso total"}

    # Cálculo base
    ingreso_disponible = ingreso_total - ahorro_deseado

    # Distribución de gastos por categorías
    distribucion = {
        "alimentación": 0.35,
        "vivienda": 0.30,
        "transporte": 0.15,
        "entretenimiento": 0.10,
        "otros": 0.10
    }

    # Verificar que la distribución suma 1.0
    if abs(sum(distribucion.values()) - 1.0) > 0.001:
        return {"error": "La distribución de categorías no suma 100%"}

    # Cálculo del monto por categoría
    gastos_detalle = {
        categoria: round(ingreso_disponible * porcentaje, 2)
        for categoria, porcentaje in distribucion.items()
    }

    # Ajustar redondeos si es necesario
    gastos_detalle = ajustar_redondeo(gastos_detalle, ingreso_disponible)

    # Cálculo de totales
    total_gastos = round(sum(gastos_detalle.values()), 2)
    total_ahorro = round(ahorro_deseado * duracion_meses, 2)
    total_ingresos = round(ingreso_total * duracion_meses, 2)

    # Estructura final del plan
    plan = {
        "nombre_plan": "Plan Financiero Automático",
        "ingreso_total": ingreso_total,
        "ahorro_deseado": ahorro_deseado,
        "duracion_meses": duracion_meses,
        "fecha_creacion": datetime.utcnow().isoformat(),
        "distribucion_gastos": gastos_detalle,
        "totales": {
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "total_ahorro": total_ahorro,
            "balance_final": round(total_ingresos - total_gastos - total_ahorro, 2)
        }
    }

    return plan

def ajustar_redondeo(gastos: Dict[str, float], total_esperado: float) -> Dict[str, float]:
    """Ajusta pequeños errores de redondeo en la distribución"""
    diferencia = round(total_esperado - sum(gastos.values()), 2)
    
    if abs(diferencia) > 0.01:
        # Ajustar en la categoría "otros" si existe, sino en la primera
        if "otros" in gastos:
            gastos["otros"] = round(gastos["otros"] + diferencia, 2)
        else:
            primera_categoria = next(iter(gastos))
            gastos[primera_categoria] = round(gastos[primera_categoria] + diferencia, 2)
    
    return gastos
    