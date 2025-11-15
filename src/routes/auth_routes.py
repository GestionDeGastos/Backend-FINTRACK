# src/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field, validator
from jose import JWTError, jwt
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from src.auth.utils import hash_password, verify_password, create_access_token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USERS_TABLE = "usuarios"

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ---------- MODELOS ACTUALIZADOS ----------
class RegisterIn(BaseModel):
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

class LoginIn(BaseModel):
    correo: EmailStr
    password: str

# ---------- FUNCIONES AUXILIARES ----------
def get_user_by_email(email: str):
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?correo=eq.{email}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al conectar con Supabase")
    data = res.json()
    return data[0] if data else None

def insert_user(nombre: str, apellido: str, edad: int, correo: str, hashed_password: str):
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}"
    payload = {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
        "correo": correo,
        "password": hashed_password,
        "fecha_registro": datetime.utcnow().isoformat()
    }
    headers_with_prefer = headers.copy()
    headers_with_prefer["Prefer"] = "return=representation"
    res = requests.post(url, headers=headers_with_prefer, json=payload)
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=res.status_code, detail="Error al registrar usuario")
    return res.json()

# ---------- ENDPOINTS ----------

@router.options("/login")
async def options_login():
    return {"status": "ok"}

@router.options("/register")
async def options_register():
    return {"status": "ok"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn):
    print(f"📝 Intentando registrar usuario: {payload.correo}")
    existing = get_user_by_email(payload.correo)
    if existing:
        print(f"❌ Usuario ya existe: {payload.correo}")
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_pw = hash_password(payload.password)
    result = insert_user(payload.nombre, payload.apellido, payload.edad, payload.correo, hashed_pw)
    print(f"✅ Usuario registrado: {payload.correo}")
    return {"msg": "Usuario registrado correctamente"}

@router.post("/login")
def login(payload: LoginIn):
    print(f"🔐 Intentando login: {payload.correo}")
    user = get_user_by_email(payload.correo)
    if not user:
        print(f"❌ Usuario no encontrado: {payload.correo}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not verify_password(payload.password, user["password"]):
        print(f"❌ Contraseña incorrecta: {payload.correo}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": user["id"], "email": user["correo"]})
    print(f"✅ Login exitoso: {payload.correo}")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{user_id}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al conectar con Supabase")
    data = res.json()
    if not data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user = data[0]
    return {
        "id": user.get("id"),
        "correo": user.get("correo"),
        "nombre": user.get("nombre"),
        "apellido": user.get("apellido"),
        "edad": user.get("edad"),
        "foto_perfil": user.get("foto_perfil"),
    }