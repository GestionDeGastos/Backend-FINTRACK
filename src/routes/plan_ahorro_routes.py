from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from src.database.supabase_client import supabase
from src.models.plan_ahorro_model import PlanAhorro, PlanAhorroUpdate
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/plan-ahorro", tags=["plan-ahorro"])

# ---------- VALIDACIONES ----------
def validar_fechas(fecha_inicio: str, fecha_fin: str) -> None:
    """
    Valida que las fechas sean válidas y que fecha_fin >= fecha_inicio
    
    Raises:
        HTTPException: Si las fechas no son válidas o están fuera de orden
    """
    try:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use formato YYYY-MM-DD (ej: 2025-11-08)"
        )
    
    if fin < inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio"
        )


def obtener_usuario_id(payload: dict) -> str:
    """
    Obtiene el usuario_id del usuario autenticado usando su correo
    
    Args:
        payload: Diccionario con el payload del token JWT
        
    Returns:
        str: El UUID del usuario
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("id").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user_result.data[0]["id"]


# ---------- ENDPOINTS ----------

@router.post("/", status_code=201)
def crear_plan_ahorro(plan: PlanAhorro, payload: dict = Depends(verify_token)):
    """
    Crea un nuevo plan de ahorro para el usuario autenticado
    
    **Parámetros:**
    - **nombre_plan**: Nombre descriptivo del plan (ej: "Vacaciones 2026")
    - **monto_objetivo**: Monto total a ahorrar (debe ser > 0)
    - **fecha_inicio**: Fecha de inicio del plan (YYYY-MM-DD)
    - **fecha_fin**: Fecha de fin del plan (YYYY-MM-DD)
    - **descripcion**: Descripción opcional del plan
    
    **Respuesta:**
    - Status 201: Plan creado exitosamente
    - Status 400: Datos inválidos (fechas o monto)
    - Status 404: Usuario no encontrado
    - Status 500: Error en la base de datos
    """
    try:
        usuario_id = obtener_usuario_id(payload)
    except HTTPException:
        raise
    
    # Validar fechas
    validar_fechas(plan.fecha_inicio, plan.fecha_fin)
    
    # Validar monto > 0
    if plan.monto_objetivo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto objetivo debe ser mayor a 0"
        )
    
    # Preparar datos para insertar
    data = {
        "usuario_id": usuario_id,
        "nombre_plan": plan.nombre_plan,
        "monto_objetivo": plan.monto_objetivo,
        "fecha_inicio": plan.fecha_inicio,
        "fecha_fin": plan.fecha_fin,
        "descripcion": plan.descripcion,
    }
    
    # Insertar en BD
    try:
        result = supabase.table("planes_ahorro").insert(data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Error al crear el plan de ahorro en la base de datos"
            )
        
        return {
            "message": "Plan de ahorro creado exitosamente",
            "data": result.data[0]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al insertar en la base de datos: {str(e)}"
        )


@router.get("/")
def obtener_planes_ahorro(payload: dict = Depends(verify_token)):
    """
    Obtiene todos los planes de ahorro del usuario autenticado
    
    **Respuesta:**
    - Lista de planes de ahorro ordenados por fecha de creación
    - Status 404: Usuario no encontrado
    """
    try:
        usuario_id = obtener_usuario_id(payload)
    except HTTPException:
        raise
    
    try:
        result = supabase.table("planes_ahorro").select("*").eq("usuario_id", usuario_id).order("creado_en", desc=True).execute()
        
        return {
            "message": "Planes de ahorro obtenidos exitosamente",
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener planes de ahorro: {str(e)}"
        )


@router.get("/{plan_id}")
def obtener_plan_ahorro(plan_id: str, payload: dict = Depends(verify_token)):
    """
    Obtiene un plan de ahorro específico
    
    **Parámetros:**
    - **plan_id**: UUID del plan a obtener
    
    **Respuesta:**
    - Status 200: Plan encontrado
    - Status 404: Plan no encontrado
    """
    try:
        usuario_id = obtener_usuario_id(payload)
    except HTTPException:
        raise
    
    try:
        result = supabase.table("planes_ahorro").select("*").eq("id", plan_id).eq("usuario_id", usuario_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Plan de ahorro no encontrado")
        
        return {
            "message": "Plan de ahorro encontrado",
            "data": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el plan: {str(e)}"
        )


@router.put("/{plan_id}")
def actualizar_plan_ahorro(plan_id: str, plan: PlanAhorroUpdate, payload: dict = Depends(verify_token)):
    """
    Actualiza un plan de ahorro existente
    
    **Parámetros:**
    - **plan_id**: UUID del plan a actualizar
    - **Campos a actualizar**: Solo se actualizan los campos proporcionados (partial update)
    
    **Respuesta:**
    - Status 200: Plan actualizado exitosamente
    - Status 400: No hay datos para actualizar o fechas inválidas
    - Status 404: Plan no encontrado
    """
    try:
        usuario_id = obtener_usuario_id(payload)
    except HTTPException:
        raise
    
    # Validar fechas si se proporcionan ambas
    if plan.fecha_inicio and plan.fecha_fin:
        validar_fechas(plan.fecha_inicio, plan.fecha_fin)
    
    # Validar monto si se proporciona
    if plan.monto_objetivo is not None and plan.monto_objetivo <= 0:
        raise HTTPException(
            status_code=400,
            detail="El monto objetivo debe ser mayor a 0"
        )
    
    # Filtrar solo los campos que se van a actualizar (no None)
    update_data = {k: v for k, v in plan.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    try:
        result = supabase.table("planes_ahorro").update(update_data).eq("id", plan_id).eq("usuario_id", usuario_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Plan de ahorro no encontrado")
        
        return {
            "message": "Plan de ahorro actualizado exitosamente",
            "data": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el plan: {str(e)}"
        )


@router.delete("/{plan_id}")
def eliminar_plan_ahorro(plan_id: str, payload: dict = Depends(verify_token)):
    """
    Elimina un plan de ahorro
    
    **Parámetros:**
    - **plan_id**: UUID del plan a eliminar
    
    **Respuesta:**
    - Status 200: Plan eliminado exitosamente
    - Status 404: Plan no encontrado
    """
    try:
        usuario_id = obtener_usuario_id(payload)
    except HTTPException:
        raise
    
    try:
        result = supabase.table("planes_ahorro").delete().eq("id", plan_id).eq("usuario_id", usuario_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Plan de ahorro no encontrado")
        
        return {
            "message": "Plan de ahorro eliminado exitosamente",
            "id": plan_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el plan: {str(e)}"
        )