from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    nombre: str
    correo: str
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None
