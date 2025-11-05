from fastapi import APIRouter, HTTPException, Depends
from src.database.supabase_client import supabase
from src.models.gastos_model import Gasto, GastoUpdate
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/gastos", tags=["gastos"])

@router.post("/", status_code=201)
def crear_gasto(gasto: Gasto, payload: dict = Depends(verify_token)):
    """Crea un nuevo gasto para el usuario autenticado"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    
    data = {
        "usuario_id": usuario_id,
        "categoria": gasto.categoria,
        "nombre_gasto": gasto.nombre_gasto,
        "monto": gasto.monto,
        "fecha": gasto.fecha,
        "descripcion": gasto.descripcion
    }
    
    result = supabase.table("gastos").insert(data).execute()
    return {
        "message": "Gasto creado con éxito",
        "data": result.data[0]
    }

@router.get("/")
def obtener_gastos(payload: dict = Depends(verify_token)):
    """Obtiene todos los gastos del usuario autenticado"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("gastos").select("*").eq("usuario_id", usuario_id).execute()
    
    return {
        "message": "Gastos obtenidos",
        "data": result.data
    }

@router.get("/{id}")
def obtener_gasto(id: str, payload: dict = Depends(verify_token)):
    """Obtiene un gasto específico"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("gastos").select("*").eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    return {
        "message": "Gasto encontrado",
        "data": result.data[0]
    }

@router.put("/{id}")
def actualizar_gasto(id: str, gasto: GastoUpdate, payload: dict = Depends(verify_token)):
    """Actualiza un gasto existente"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    update_data = {k: v for k, v in gasto.dict().items() if v is not None}
    
    result = supabase.table("gastos").update(update_data).eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    return {
        "message": "Gasto actualizado con éxito",
        "data": result.data[0]
    }

@router.delete("/{id}")
def eliminar_gasto(id: str, payload: dict = Depends(verify_token)):
    """Elimina un gasto"""
    user_email = payload["sub"]
    user_result = supabase.table("usuarios").select("identificación").eq("correo", user_email).execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_id = user_result.data[0]["identificación"]
    result = supabase.table("gastos").delete().eq("identificación", id).eq("usuario_id", usuario_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    return {
        "message": "Gasto eliminado con éxito",
        "id": id
    }