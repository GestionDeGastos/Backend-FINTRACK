# src/routes/perfil_routes.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from src.middleware.auth_middleware import verify_token
from src.models.perfil_model import PerfilUpdate, PerfilResponse
from src.services.perfil_service import (
    obtener_perfil,
    actualizar_perfil,
    subir_foto_perfil,
    eliminar_foto_perfil
)

router = APIRouter(prefix="/perfil", tags=["Perfil"])


@router.get("/", response_model=PerfilResponse)
def get_perfil(payload: dict = Depends(verify_token)):
    """Obtiene el perfil del usuario autenticado"""
    usuario_id = payload["sub"]
    return obtener_perfil(usuario_id)


@router.patch("/", response_model=PerfilResponse)
def update_perfil(data: PerfilUpdate, payload: dict = Depends(verify_token)):
    """
    Actualiza parcialmente el perfil del usuario.
    Permite modificar: nombre, apellido, edad y/o contraseña.
    """
    usuario_id = payload["sub"]
    
    if not any([data.nombre, data.apellido, data.edad, data.password]):
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un campo para actualizar"
        )
    
    return actualizar_perfil(usuario_id, data.nombre, data.apellido, data.edad, data.password)


@router.post("/foto")
def upload_foto(file: UploadFile = File(...), payload: dict = Depends(verify_token)):
    """
    Sube una foto de perfil.
    Formatos permitidos: JPEG, JPG, PNG, WEBP
    Tamaño máximo: 5MB
    """
    usuario_id = payload["sub"]
    
    if not file:
        raise HTTPException(status_code=400, detail="Debe proporcionar un archivo")
    
    foto_url = subir_foto_perfil(usuario_id, file)
    
    return {
        "mensaje": "Foto de perfil actualizada correctamente",
        "foto_url": foto_url
    }


@router.delete("/foto")
def delete_foto(payload: dict = Depends(verify_token)):
    """Elimina la foto de perfil del usuario"""
    usuario_id = payload["sub"]
    return eliminar_foto_perfil(usuario_id)