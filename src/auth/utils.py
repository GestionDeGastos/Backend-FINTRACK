from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables del archivo .env
load_dotenv()

# Configuración de hashing y JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# ---------- FUNCIONES DE HASH Y VERIFICACIÓN ----------
def hash_password(password: str) -> str:
    """Genera el hash seguro de una contraseña."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)

# ---------- FUNCIÓN PARA CREAR TOKENS ----------
def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Crea un token JWT con expiración automática.
    Por defecto dura 60 minutos (1 hora), configurable desde .env
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta if expires_delta else ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt