from fastapi import APIRouter, Depends, HTTPException
from src.middleware.auth_middleware import verify_token
from src.schemas.planGestion_schema import PlanGestionSchema
from src.services.plan_gestion_service import generar_plan
from src.database.supabase_client import supabase

router = APIRouter(prefix="/api/plan-gestion", tags=["Plan de Gestión"])


# CREAR PLAN DE GESTIÓN
@router.post("/")
async def crear_plan_gestion(data: PlanGestionSchema, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    # Generar el plan financiero con la lógica existente
    plan = generar_plan(
        ingreso_total=data.ingreso_total,
        ahorro_deseado=data.ahorro_deseado or 0,
        duracion_meses=data.duracion_meses
    )

    # Verificar si hubo error en la generación
    if "error" in plan:
        raise HTTPException(status_code=400, detail=plan["error"])

    # Guardar el plan en Supabase
    nuevo_plan = {
    "usuario_id": usuario_id,
    "nombre_plan": data.nombre_plan,
    "ingreso_total": data.ingreso_total,
    "ahorro_deseado": data.ahorro_deseado or 0,
    "duracion_meses": data.duracion_meses, 
    "distribucion_gastos": plan["distribucion_gastos"],
}


    try:
        response = supabase.table("plan_gestion").insert(nuevo_plan).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="No se pudo guardar el plan en la base de datos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando el plan: {str(e)}")

    # Retornar el plan completo al frontend
    return {
        "mensaje": "Plan de gestión creado correctamente",
        "plan": plan
    }


# OBTENER TODOS LOS PLANES DE UN USUARIO
@router.get("/")
async def listar_planes(payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    try:
        response = supabase.table("plan_gestion").select("*").eq("usuario_id", usuario_id).execute()
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo planes: {str(e)}")


# OBTENER DETALLE DE UN PLAN POR ID
@router.get("/{plan_id}")
async def detalle_plan(plan_id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    try:
        response = supabase.table("plan_gestion").select("*").eq("id", plan_id).eq("usuario_id", usuario_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo plan: {str(e)}")
