from fastapi import APIRouter, Depends, HTTPException
from src.middleware.auth_middleware import verify_token
from src.schemas.plan_gestion_schemas import PlanGestionCreate
from src.services.plan_gestion_service import crear_plan, obtener_planes, obtener_plan_por_id

router = APIRouter(prefix="/api/plan-gestion", tags=["Plan de Gestión"])

@router.post("/")
async def crear_plan_gestion(data: PlanGestionCreate, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    try:
        return await crear_plan(usuario_id, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def listar_planes(payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    return await obtener_planes(usuario_id)

@router.get("/{plan_id}")
async def detalle_plan(plan_id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]
    return await obtener_plan_por_id(usuario_id, plan_id)
