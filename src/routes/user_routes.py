from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from src.database.supabase_client import supabase
from src.models.user_model import Usuario, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/")
def crear_usuario(usuario: Usuario):
    existing = supabase.table("usuarios").select("*").eq("correo", usuario.correo).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="El correo ingresado ya está registrado")
    
    hashed_password = pwd_context.hash(usuario.password)
    data = {**usuario.dict(), "password": hashed_password}
    result = supabase.table("usuarios").insert(data).execute()
    return {"message": "Usuario creado con éxito", "data": result.data}

@router.get("/{id}")
def obtener_usuario(id: str):
    result = supabase.table("usuarios").select("*").eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return result.data[0]

@router.put("/{id}")
def actualizar_usuario(id: str, usuario: UsuarioUpdate):
    update_data = {k: v for k, v in usuario.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password"] = pwd_context.hash(update_data["password"])
    result = supabase.table("usuarios").update(update_data).eq("id", id).execute()
    return {"message": "Usuario actualizado con éxito", "data": result.data}

@router.delete("/{id}")
def eliminar_usuario(id: str):
    result = supabase.table("usuarios").delete().eq("id", id).execute()
    return {"message": "Usuario eliminado con éxito", "data": result.data}

