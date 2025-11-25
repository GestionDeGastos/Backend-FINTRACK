# src/routes/user_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field, validator
from src.database.supabase_client import supabase
from src.auth.utils import hash_password
from src.middleware.auth_middleware import verify_token
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

# ========== MODELOS ==========

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    edad: int = Field(..., ge=18, le=120)
    correo: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('edad')
    def validate_edad(cls, v):
        if v < 18:
            raise ValueError('Debes ser mayor de 18 años para registrarte')
        if v > 120:
            raise ValueError('Edad no válida')
        return v

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    edad: Optional[int] = Field(None, ge=18, le=120)
    correo: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    
    @validator('edad')
    def validate_edad(cls, v):
        if v is not None and (v < 18 or v > 120):
            raise ValueError('La edad debe estar entre 18 y 120 años')
        return v

# ========== ENDPOINTS ==========

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_usuario(user: UsuarioCreate):
    """
    Crea un nuevo usuario con todos los campos requeridos.
    Requiere: nombre, apellido, edad (18+), correo y contraseña (8+ caracteres)
    """
    
    # Verificar si el usuario ya existe
    existing = supabase.table("usuarios").select("id").eq("correo", user.correo).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Crear usuario
    new_user = {
        "nombre": user.nombre,
        "apellido": user.apellido,
        "edad": user.edad,
        "correo": user.correo,
        "password": hash_password(user.password),
        "fecha_registro": datetime.utcnow().isoformat()
    }
    
    try:
        result = supabase.table("usuarios").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Error al crear usuario")
        
        usuario_creado = result.data[0]
        
        return {
            "mensaje": "Usuario creado correctamente",
            "usuario": {
                "id": usuario_creado["id"],
                "nombre": usuario_creado["nombre"],
                "apellido": usuario_creado["apellido"],
                "edad": usuario_creado["edad"],
                "correo": usuario_creado["correo"],
                "fecha_registro": usuario_creado["fecha_registro"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")


@router.get("/")
def listar_usuarios():
    """
    Lista todos los usuarios registrados (sin mostrar contraseñas).
    """
    try:
        result = supabase.table("usuarios").select(
            "id, nombre, apellido, edad, correo, foto_perfil, fecha_registro, updated_at"
        ).execute()
        
        return {
            "total": len(result.data),
            "usuarios": result.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: str):
    """
    Obtiene los datos de un usuario específico por su ID.
    No devuelve la contraseña.
    """
    try:
        result = supabase.table("usuarios").select(
            "id, nombre, apellido, edad, correo, foto_perfil, fecha_registro, updated_at"
        ).eq("id", usuario_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: str, user: UsuarioUpdate, payload: dict = Depends(verify_token)):
    """
    Actualiza los datos de un usuario existente.
    Requiere autenticación. Solo puede actualizar su propio perfil.
    """
    # Verificar que el usuario autenticado solo pueda actualizar su propio perfil
    user_id_from_token = payload.get("sub")
    
    if user_id_from_token != usuario_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para actualizar este usuario"
        )
    
    # Preparar datos para actualizar
    update_data = {}
    
    if user.nombre:
        update_data["nombre"] = user.nombre
    
    if user.apellido:
        update_data["apellido"] = user.apellido
    
    if user.edad:
        update_data["edad"] = user.edad
    
    if user.correo:
        # Verificar que el nuevo correo no esté en uso
        existing = supabase.table("usuarios").select("id").eq("correo", user.correo).execute()
        if existing.data and existing.data[0]["id"] != usuario_id:
            raise HTTPException(status_code=400, detail="El correo ya está en uso")
        update_data["correo"] = user.correo
    
    if user.password:
        update_data["password"] = hash_password(user.password)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    
    try:
        result = supabase.table("usuarios").update(update_data).eq("id", usuario_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Obtener datos actualizados sin contraseña
        updated_user = supabase.table("usuarios").select(
            "id, nombre, apellido, edad, correo, foto_perfil, fecha_registro, updated_at"
        ).eq("id", usuario_id).execute()
        
        return {
            "mensaje": "Usuario actualizado correctamente",
            "usuario": updated_user.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: str, payload: dict = Depends(verify_token)):
    """
    Elimina un usuario de la base de datos.
    Requiere autenticación. Solo puede eliminar su propio perfil.
    """
    # Verificar que el usuario autenticado solo pueda eliminar su propio perfil
    user_id_from_token = payload.get("sub")
    
    if user_id_from_token != usuario_id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para eliminar este usuario"
        )
    
    try:
        # Verificar que el usuario existe
        existing = supabase.table("usuarios").select("id").eq("id", usuario_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Eliminar usuario
        result = supabase.table("usuarios").delete().eq("id", usuario_id).execute()
        
        return {
            "mensaje": "Usuario eliminado correctamente",
            "id": usuario_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")