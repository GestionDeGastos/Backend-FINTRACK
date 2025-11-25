from typing import Dict, Any
from src.database.supabase_client import supabase
from src.services.analisis_plan_service import analizar_plan

def validar_y_convertir_porcentajes(porcentajes: Dict[str, float]) -> Dict[str, float]:
    """
    Valida que la suma de porcentajes sea 100 (con pequeño margen)
    y los convierte a fracciones (0.0 - 1.0).
    """
    valores = {k: float(v) for k, v in porcentajes.items()}
    suma = sum(valores.values())

    if abs(suma - 100.0) > 0.5:
        raise ValueError(f"La suma de porcentajes debe ser 100%. Actualmente es {suma}")

    fracciones = {k: round(v / 100.0, 4) for k, v in valores.items()}
    return fracciones


def personalizar_plan(plan_id: str, usuario_id: str, porcentajes_input: Dict[str, float]) -> Dict[str, Any]:
    """
    Personaliza un plan existente.
    Ahora cualquier plan es editable sin importar gastos extraordinarios.
    Guarda:
    - porcentajes_personalizados (100%)
    - distribucion_gastos recalculada
    - editable siempre en TRUE
    """

    # Obtener plan existente
    resp = supabase.table("plan_gestion").select("*").eq("id", plan_id).eq("usuario_id", usuario_id).execute()
    if not resp.data:
        raise Exception("Plan no encontrado")

    plan = resp.data[0]

    # YA NO SE VERIFICA, Siempre es Editable
    # Validar porcentajes
    porcentajes = validar_y_convertir_porcentajes(porcentajes_input)

    ingreso_total = plan.get("ingreso_total", 0)
    ahorro = plan.get("ahorro_deseado", 0)
    ingreso_disponible = ingreso_total - (ahorro or 0)

    # Convertir fracciones a montos reales
    distribucion_montos = {k: round(ingreso_disponible * v, 2) for k, v in porcentajes.items()}

    # Payload para actualizar
    update_payload = {
        "porcentajes_personalizados": {k: round(v * 100, 2) for k, v in porcentajes.items()},
        "distribucion_gastos": distribucion_montos,
        "editable": True     # SIEMPRE EDITABLE
    }

    # Actualizar en Supabase
    update = supabase.table("plan_gestion").update(update_payload).eq("id", plan_id).eq("usuario_id", usuario_id).execute()

    if not update.data:
        raise Exception("No se pudo actualizar el plan")

    new_plan = update.data[0]
    analisis = analizar_plan(new_plan)

    return {"plan": new_plan, "analisis": analisis}
    
