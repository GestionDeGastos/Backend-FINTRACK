# src/middleware/auth_middleware.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Inicializar esquema HTTPBearer (para que Swagger lo reconozca correctamente)
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware que valida el token JWT incluido en el encabezado Authorization.
    Usa el esquema Bearer para Swagger.
    """
    token = credentials.credentials  # Extrae el token del header "Authorization: Bearer <token>"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
