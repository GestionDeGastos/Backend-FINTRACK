from typing import Dict, Any
from src.database.supabase_client import supabase

def agregar_gasto_extra(plan_id: int, usuario_id: str, gasto_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserta un gasto marcado como extraordinario, recalcula la suma de
    gastos extraordinarios del plan y actualiza plan_gestion.saldo y editable.
    gasto_payload debe contener: monto, nombre_gasto, fecha (ISO), descripcion
    """

    # 1) Insertar gasto en la tabla gastos con extraordinario = true y plan_id
    insert_payload = {
        "plan_id": plan_id,
        "usuario_id": usuario_id,
        "nombre_gasto": gasto_payload.get("nombre_gasto"),
        "monto": gasto_payload["monto"],
        "fecha": gasto_payload["fecha"],
        "descripcion": gasto_payload.get("descripcion"),
        "extraordinario": True
    }

    insert_res = supabase.table("gastos").insert(insert_payload).execute()
    if insert_res.status_code not in (200, 201) or not insert_res.data:
        raise Exception("No se pudo insertar el gasto extraordinario")

    # 2) Calcular total de gastos extraordinarios para ese plan
    gastos_res = supabase.table("gastos")\
        .select("monto")\
        .eq("plan_id", plan_id)\
        .eq("extraordinario", True)\
        .execute()

    gastos_list = gastos_res.data or []
    total_extra = sum([float(g.get("monto", 0)) for g in gastos_list])

    # 3) Obtener plan actual
    plan_res = supabase.table("plan_gestion").select("*").eq("id", plan_id).execute()
    if not plan_res.data:
        raise Exception("Plan no encontrado")

    plan = plan_res.data[0]
    ingreso_inicial = float(plan.get("ingreso_total", 0))

    # 4) Recalcular saldo = ingreso_inicial - total_extra
    nuevo_saldo = round(ingreso_inicial - total_extra, 2)

    # 5) Actualizar plan: saldo y editable = true (permitir personalizar luego)
    update_payload = {
        "saldo": nuevo_saldo,
        "editable": True
    }

    update_res = supabase.table("plan_gestion").update(update_payload).eq("id", plan_id).execute()
    if update_res.status_code not in (200, 201):
        raise Exception("No se pudo actualizar el plan con el nuevo saldo")

    # 6) Devolver resumen
    return {
        "mensaje": "Gasto extraordinario registrado y plan actualizado",
        "gasto": insert_res.data[0],
        "total_extraordinarios": total_extra,
        "nuevo_saldo": nuevo_saldo
    }
