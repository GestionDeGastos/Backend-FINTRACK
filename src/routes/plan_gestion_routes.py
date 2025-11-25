from fastapi import APIRouter, Depends, HTTPException
from src.middleware.auth_middleware import verify_token
from src.schemas.planGestion_schema import PlanGestionSchema
from src.schemas.plan_personalizar_schema import PlanPersonalizarSchema
from src.services.plan_gestion_service import generar_plan
from src.services.plan_personalizar_service import personalizar_plan
from src.services.analisis_plan_service import analizar_plan
from src.database.supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/api/plan-gestion", tags=["Plan de Gestión"])


# ================================================================
# CREAR PLAN
# ================================================================
@router.post("/")
async def crear_plan_gestion(data: PlanGestionSchema, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    plan = generar_plan(
        ingreso_total=data.ingreso_total,
        ahorro_deseado=data.ahorro_deseado or 0,
        duracion_meses=data.duracion_meses
    )

    if "error" in plan:
        raise HTTPException(status_code=400, detail=plan["error"])

    nuevo_plan = {
        "usuario_id": usuario_id,
        "nombre_plan": data.nombre_plan,
        "ingreso_total": data.ingreso_total,
        "ahorro_deseado": data.ahorro_deseado or 0,
        "duracion_meses": data.duracion_meses,
        "distribucion_gastos": plan["distribucion_gastos"],
        "editable": False,
        "porcentajes_personalizados": None,
        "saldo": data.ingreso_total - (data.ahorro_deseado or 0)
    }

    res = supabase.table("plan_gestion").insert(nuevo_plan).execute()

    if not res.data:
        raise HTTPException(status_code=500, detail="No se pudo guardar el plan")

    return {"mensaje": "Plan creado", "plan": res.data[0]}

# ================================================================
# LISTAR PLANES
# ================================================================
@router.get("/")
async def listar_planes(payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    res = supabase.table("plan_gestion").select("*").eq("usuario_id", usuario_id).execute()
    return res.data or []


# ================================================================
# ANALISIS DEL PLAN
# ================================================================
@router.get("/{plan_id}/analisis")
async def analizar_plan_endpoint(plan_id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    res = (
        supabase.table("plan_gestion")
        .select("*")
        .eq("id", plan_id)
        .eq("usuario_id", usuario_id)
        .single()
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    plan_data = res.data
    analisis = analizar_plan(plan_data)

    return {"mensaje": "Análisis generado", "plan_id": plan_id, "analisis": analisis}

# REGISTRAR INGRESO EXTRA

@router.post("/ingresos_extra/{plan_id}")
def registrar_ingreso_extra(plan_id: int, data: dict, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    monto = data.get("monto")

    if not monto or monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")

    ingreso_data = {
        "usuario_id": usuario_id,
        "concepto": "Ingreso Extra",
        "nombre_fuente": "Ingreso adicional",
        "monto": monto,
        "fecha": data.get("fecha") or datetime.utcnow().isoformat(),
        "descripcion": "Ingreso extraordinario registrado desde personalización"
    }

    supabase.table("ingresos").insert(ingreso_data).execute()

    plan = (
        supabase.table("plan_gestion")
        .select("*")
        .eq("id", plan_id)
        .single()
        .execute()
    ).data

    nuevo_ingreso = plan["ingreso_total"] + monto
    ingreso_disponible = nuevo_ingreso - plan["ahorro_deseado"]

    # Recalcular distribución proporcional
    distrib = plan["distribucion_gastos"]
    total_original = sum(distrib.values()) or 1

    nueva_distribucion = {
        cat: round(ingreso_disponible * (val / total_original), 2)
        for cat, val in distrib.items()
    }

    nuevo_saldo = ingreso_disponible - sum(nueva_distribucion.values())

    supabase.table("plan_gestion").update({
        "ingreso_total": nuevo_ingreso,
        "distribucion_gastos": nueva_distribucion,
        "saldo": nuevo_saldo
    }).eq("id", plan_id).execute()

    return {"mensaje": "Ingreso extra registrado", "saldo": nuevo_saldo}

# REGISTRAR GASTO EXTRA 

@router.post("/gastos_extra/{plan_id}")
async def registrar_gasto_extra(plan_id: str, body: dict, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    monto = body.get("monto")

    if not monto or monto <= 0:
        raise HTTPException(status_code=400, detail="Monto inválido")

    plan = (
        supabase.table("plan_gestion")
        .select("*")
        .eq("id", plan_id)
        .single()
        .execute()
    ).data

    ingreso_total = float(plan["ingreso_total"])
    ahorro = float(plan["ahorro_deseado"])
    distrib = plan["distribucion_gastos"]
    porcentajes = plan.get("porcentajes_personalizados")

    #  Nuevo ingreso total REAL
    nuevo_ingreso_total = ingreso_total - monto
    if nuevo_ingreso_total < 0:
        nuevo_ingreso_total = 0

    # Ingreso disponible después del gasto
    ingreso_disponible = nuevo_ingreso_total - ahorro
    if ingreso_disponible < 0:
        ingreso_disponible = 0

    # Recalcular distribución proporcional a porcentajes o distribución original
    nueva_distribucion = {}

    if porcentajes:
        # Si el usuario ya personalizó → usar porcentajes personalizados
        for cat, pct in porcentajes.items():
            nueva_distribucion[cat] = round(ingreso_disponible * (pct / 100), 2)
    else:
        # Si no, usar distribución original proporcionalmente
        total_original = sum(distrib.values()) or 1
        for cat, val in distrib.items():
            nueva_distribucion[cat] = round(ingreso_disponible * (val / total_original), 2)

    nuevo_saldo = ingreso_disponible - sum(nueva_distribucion.values())

    supabase.table("plan_gestion").update({
        "ingreso_total": nuevo_ingreso_total,
        "distribucion_gastos": nueva_distribucion,
        "saldo": nuevo_saldo,
        "editable": True
    }).eq("id", plan_id).execute()

    return {"mensaje": "Gasto extra registrado", "saldo": nuevo_saldo}



# ================================================================
# PERSONALIZAR PORCENTAJES
# ================================================================
@router.put("/{plan_id}/personalizar")
async def personalizar_porcentajes(plan_id: int, body: dict, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    porcentajes = body.get("porcentajes")
    if not porcentajes:
        raise HTTPException(status_code=400, detail="Faltan porcentajes")

    total_pct = sum(porcentajes.values())
    if abs(total_pct - 100) > 0.1:
        raise HTTPException(status_code=400, detail="Los porcentajes deben sumar 100%")

    plan = (
        supabase.table("plan_gestion")
        .select("*")
        .eq("id", plan_id)
        .eq("usuario_id", usuario_id)
        .single()
        .execute()
    ).data

    ingreso_total = float(plan["ingreso_total"])
    ahorro = float(plan["ahorro_deseado"])
    ingreso_total_real = ingreso_total  # ya viene ajustado por gastos extra
    ingreso_disponible = ingreso_total_real - ahorro


    nueva_distribucion = {
        cat: round(ingreso_disponible * (pct / 100), 2)
        for cat, pct in porcentajes.items()
    }

    saldo = ingreso_disponible - sum(nueva_distribucion.values())

    supabase.table("plan_gestion").update({
        "distribucion_gastos": nueva_distribucion,
        "porcentajes_personalizados": porcentajes,
        "saldo": saldo,
        "editable": True
    }).eq("id", plan_id).execute()

    return {
        "mensaje": "Plan personalizado correctamente",
        "distribucion_gastos": nueva_distribucion,
        "saldo": saldo
    }

@router.get("/{plan_id}")
async def obtener_plan(plan_id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    res = (
        supabase.table("plan_gestion")
        .select("id, usuario_id, nombre_plan, ingreso_total, ahorro_deseado, duracion_meses, distribucion_gastos, porcentajes_personalizados, saldo")
        .eq("id", plan_id)
        .eq("usuario_id", usuario_id)
        .single()
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    return res.data
# ================================================================
# ELIMINAR PLAN
# ================================================================
@router.delete("/{plan_id}")
async def eliminar_plan(plan_id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    # Verificar que el plan exista y sea del usuario
    res = (
        supabase.table("plan_gestion")
        .select("*")
        .eq("id", plan_id)
        .eq("usuario_id", usuario_id)
        .single()
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    # Eliminar el plan
    supabase.table("plan_gestion").delete().eq("id", plan_id).execute()

    return {"mensaje": "Plan eliminado correctamente"}
