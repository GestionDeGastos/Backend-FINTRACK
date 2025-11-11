from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.schemas.plan_gestion_schemas import PlanGestionCreate, PlanGestionResp
from src.services.plan_gestion_service import (
    crear_plan,
    obtener_planes,
    obtener_plan_por_id,
    actualizar_plan,
    eliminar_plan,
)
from src.middleware.auth_middleware import verify_token

# Inicializa el router
router = APIRouter(
    prefix="/api/plan-gestion",
    tags=["Plan de Gestión de Gastos"],
    responses={404: {"description": "No encontrado"}}
)

# --------------------------------------------
# 🟩 Crear un nuevo plan de gestión
# --------------------------------------------
@router.post("/", response_model=PlanGestionResp)
def crear_plan_endpoint(plan: PlanGestionCreate, payload: dict = Depends(verify_token)):
    """
    Crea un nuevo plan de gestión de gasto asociado al usuario autenticado.
    """
    usuario_id = payload.get("sub")
    nuevo_plan = crear_plan(usuario_id, plan.dict())
    if not nuevo_plan:
        raise HTTPException(status_code=400, detail="No se pudo crear el plan de gestión.")
    return nuevo_plan


# --------------------------------------------
# 🟦 Obtener todos los planes del usuario
# --------------------------------------------
@router.get("/", response_model=List[PlanGestionResp])
def obtener_planes_endpoint(payload: dict = Depends(verify_token)):
    """
    Obtiene todos los planes de gestión creados por el usuario autenticado.
    """
    usuario_id = payload.get("sub")
    planes = obtener_planes(usuario_id)
    return planes


# --------------------------------------------
# 🟨 Obtener un plan específico por ID
# --------------------------------------------
@router.get("/{plan_id}", response_model=PlanGestionResp)
def obtener_plan_por_id_endpoint(plan_id: int, payload: dict = Depends(verify_token)):
    """
    Obtiene la información de un plan de gestión específico.
    """
    usuario_id = payload.get("sub")
    plan = obtener_plan_por_id(plan_id, usuario_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado o sin permisos.")
    return plan


# --------------------------------------------
# 🟧 Actualizar un plan existente
# --------------------------------------------
@router.put("/{plan_id}", response_model=PlanGestionResp)
def actualizar_plan_endpoint(plan_id: int, plan: PlanGestionCreate, payload: dict = Depends(verify_token)):
    """
    Actualiza un plan de gestión existente (solo si pertenece al usuario autenticado).
    """
    usuario_id = payload.get("sub")
    actualizado = actualizar_plan(plan_id, usuario_id, plan.dict())
    if not actualizado:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el plan (no encontrado o sin permisos).")
    return actualizado


# --------------------------------------------
# 🟥 Eliminar un plan existente
# --------------------------------------------
@router.delete("/{plan_id}")
def eliminar_plan_endpoint(plan_id: int, payload: dict = Depends(verify_token)):
    """
    Elimina un plan de gestión de gastos (solo si pertenece al usuario autenticado).
    """
    usuario_id = payload.get("sub")
    eliminado = eliminar_plan(plan_id, usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Plan no encontrado o sin permisos para eliminarlo.")
    return {"mensaje": "🗑️ Plan eliminado correctamente."}
