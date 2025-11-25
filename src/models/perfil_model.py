# src/models/perfil_model.py
from pydantic import BaseModel, Field, validator
from typing import Optional

class PerfilUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    edad: Optional[int] = Field(None, ge=18, le=120)
    password: Optional[str] = Field(None, min_length=8)
    
    @validator('edad')
    def validate_edad(cls, v):
        if v is not None and (v < 18 or v > 120):
            raise ValueError('La edad debe estar entre 18 y 120 años')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class PerfilResponse(BaseModel):
    id: str
    nombre: str
    apellido: Optional[str] = None
    edad: Optional[int] = None
    correo: str
    foto_perfil: Optional[str] = None
    fecha_registro: str
    updated_at: Optional[str] = None