from fastapi import APIRouter, HTTPException, Depends
from src.middleware.auth_middleware import verify_token
from src.database.supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/gastos", tags=["gastos"])

# ================================================================
# POST /gastos_extra/{plan_id}
# ================================================================
@router.post("/gastos_extra/{plan_id}")
async def registrar_gasto_extra(plan_id: str, body: dict, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    monto = body.get("monto")

    if not monto or monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")

    # Obtener plan
    plan_res = supabase.table("plan_gestion").select("*").eq("id", plan_id).single().execute()
    if not plan_res.data:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    plan = plan_res.data
    
    ingreso = float(plan["ingreso_total"])
    ahorro = float(plan["ahorro_deseado"])
    distrib = dict(plan["distribucion_gastos"])

    # Registrar gasto real
    saldo_anterior = float(plan.get("saldo", ingreso - ahorro))

    nuevo_saldo = saldo_anterior - monto

    # Reducir desde distribución (solo si quieres reflejarlo ahí)
    if "Otros" in distrib:
        distrib["Otros"] = max(0, float(distrib["Otros"]) - monto)

    # Guardar cambios
    supabase.table("plan_gestion").update({
        "distribucion_gastos": distrib,
        "saldo": nuevo_saldo
    }).eq("id", plan_id).execute()

    return {
        "mensaje": "Gasto extra registrado correctamente",
        "saldo_anterior": saldo_anterior,
        "saldo_nuevo": nuevo_saldo
    }
