from fastapi import APIRouter, HTTPException, Depends
from src.database.supabase_client import supabase
from src.models.ingresos_model import Ingreso, IngresoUpdate
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/ingresos", tags=["ingresos"])

@router.post("/", status_code=201)
def crear_ingreso(ingreso: Ingreso, payload: dict = Depends(verify_token)):
    """Crea un nuevo ingreso para el usuario autenticado"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    
    data = {
        "usuario_id": usuario_id,
        "concepto": ingreso.concepto,
        "nombre_fuente": ingreso.nombre_fuente,
        "monto": ingreso.monto,
        "fecha": ingreso.fecha,
        "descripcion": ingreso.descripcion
    }
    
    result = supabase.table("ingresos").insert(data).execute()
    return {
        "message": "Ingreso creado con éxito",
        "data": result.data[0]
    }

@router.get("/")
def obtener_ingresos(payload: dict = Depends(verify_token)):
    """Obtiene todos los ingresos del usuario autenticado"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("ingresos").select("*").eq("usuario_id", usuario_id).execute()
    
    return {
        "message": "Ingresos obtenidos",
        "data": result.data
    }

@router.get("/{id}")
def obtener_ingreso(id: str, payload: dict = Depends(verify_token)):
    """Obtiene un ingreso específico"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("ingresos").select("*").eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    
    return {
        "message": "Ingreso encontrado",
        "data": result.data[0]
    }

@router.put("/{id}")
def actualizar_ingreso(id: str, ingreso: IngresoUpdate, payload: dict = Depends(verify_token)):
    """Actualiza un ingreso existente"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    update_data = {k: v for k, v in ingreso.dict().items() if v is not None}
    
    result = supabase.table("ingresos").update(update_data).eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    
    return {
        "message": "Ingreso actualizado con éxito",
        "data": result.data[0]
    }

@router.delete("/{id}")
def eliminar_ingreso(id: str, payload: dict = Depends(verify_token)):
    """Elimina un ingreso"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("ingresos").delete().eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    
    return {
        "message": "Ingreso eliminado con éxito",
        "id": id
    }