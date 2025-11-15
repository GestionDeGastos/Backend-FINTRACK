# src/services/perfil_service.py
from fastapi import UploadFile, HTTPException
from src.database.supabase_client import supabase
from src.auth.utils import hash_password
import uuid
from typing import Optional, Dict

BUCKET_NAME = "profile-pictures"

def obtener_perfil(usuario_id: str) -> Dict:
    """Obtiene los datos del perfil del usuario"""
    try:
        response = supabase.table("usuarios").select("*").eq("id", usuario_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        usuario = response.data[0]
        
        return {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "apellido": usuario.get("apellido"),
            "edad": usuario.get("edad"),
            "correo": usuario["correo"],
            "foto_perfil": usuario.get("foto_perfil"),
            "fecha_registro": usuario["fecha_registro"],
            "updated_at": usuario.get("updated_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfil: {str(e)}")


def actualizar_perfil(
    usuario_id: str, 
    nombre: Optional[str], 
    apellido: Optional[str],
    edad: Optional[int],
    password: Optional[str]
) -> Dict:
    """Actualiza los datos del perfil del usuario"""
    try:
        update_data = {}
        
        if nombre:
            update_data["nombre"] = nombre
        
        if apellido:
            update_data["apellido"] = apellido
        
        if edad:
            if edad < 18 or edad > 120:
                raise HTTPException(status_code=400, detail="La edad debe estar entre 18 y 120 años")
            update_data["edad"] = edad
        
        if password:
            if len(password) < 8:
                raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
            update_data["password"] = hash_password(password)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        response = supabase.table("usuarios").update(update_data).eq("id", usuario_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return obtener_perfil(usuario_id)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil: {str(e)}")


def subir_foto_perfil(usuario_id: str, file: UploadFile) -> str:
    """Sube la foto de perfil a Supabase Storage y actualiza la URL en la BD"""
    try:
        # Validar tipo de archivo
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Use: {', '.join(allowed_types)}"
            )
        
        # Validar tamaño (5MB máximo)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="El archivo no debe superar 5MB")
        
        # Generar nombre único
        extension = file.filename.split(".")[-1]
        file_name = f"{usuario_id}_{uuid.uuid4()}.{extension}"
        file_path = f"profiles/{file_name}"
        
        # Leer contenido
        file_content = file.file.read()
        
        # Subir a Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Obtener URL pública
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        
        # Actualizar BD
        supabase.table("usuarios").update({"foto_perfil": public_url}).eq("id", usuario_id).execute()
        
        return public_url
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subiendo foto: {str(e)}")


def eliminar_foto_perfil(usuario_id: str) -> Dict:
    """Elimina la foto de perfil del usuario"""
    try:
        usuario = supabase.table("usuarios").select("foto_perfil").eq("id", usuario_id).execute()
        
        if not usuario.data or not usuario.data[0].get("foto_perfil"):
            raise HTTPException(status_code=404, detail="No hay foto de perfil para eliminar")
        
        foto_url = usuario.data[0]["foto_perfil"]
        file_path = foto_url.split(f"{BUCKET_NAME}/")[-1]
        
        supabase.storage.from_(BUCKET_NAME).remove([file_path])
        supabase.table("usuarios").update({"foto_perfil": None}).eq("id", usuario_id).execute()
        
        return {"mensaje": "Foto de perfil eliminada correctamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando foto: {str(e)}")