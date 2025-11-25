# src/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

from src.auth.utils import hash_password, verify_password, create_access_token, generate_recovery_token, verify_recovery_token

from src.middleware.auth_middleware import verify_token

from src.auth.email_sender import send_recovery_email
from src.auth.utils import generate_recovery_token, verify_recovery_token
from src.models.auth_models import RecoverRequest, ResetRequest, ChangePasswordRequest

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_KEY = os.getenv("ADMIN_KEY", "tu_clave_secreta_aqui")
USERS_TABLE = "usuarios"

router = APIRouter(prefix="/auth", tags=["Auth"])

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ---------- MODELOS ----------

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


class RegisterAdminIn(BaseModel):
    """Modelo para registrar un admin (requiere clave de admin)"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    edad: int = Field(..., ge=18, le=120)
    correo: EmailStr
    password: str = Field(..., min_length=8)
    admin_key: str = Field(..., description="Clave secreta para registrar admin")
    
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


class PromoteUserIn(BaseModel):
    admin_key: str = Field(..., description="Clave secreta de admin")


# ---------- FUNCIONES AUXILIARES ----------

def get_user_by_email(email: str):
    """
    Obtiene al usuario por correo desde Supabase.
    Incluye el rol en la respuesta.
    """
    url = (
        f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}"
        f"?select=id,correo,password,nombre,apellido,edad,foto_perfil,rol&correo=eq.{email}"
    )
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al conectar con Supabase")

    data = res.json()
    return data[0] if data else None


def insert_user(nombre: str, apellido: str, edad: int, correo: str, hashed_password: str, rol: str = "user"):
    """
    Inserta un usuario nuevo en Supabase con su rol.
    """
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}"
    payload = {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
        "correo": correo,
        "password": hashed_password,
        "rol": rol,  # user o admin
        "fecha_registro": datetime.utcnow().isoformat(),
    }
    headers_with_prefer = headers.copy()
    headers_with_prefer["Prefer"] = "return=representation"
    res = requests.post(url, headers=headers_with_prefer, json=payload)

    if res.status_code not in (200, 201):
        raise HTTPException(
            status_code=res.status_code, detail="Error al registrar usuario"
        )

    return res.json()


def get_user_by_id(user_id: str):
    """
    Obtiene un usuario por su ID.
    """
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{user_id}"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Error al conectar con Supabase")
    
    data = res.json()
    return data[0] if data else None


# ---------- ENDPOINTS ----------

@router.options("/login")
async def options_login():
    return {"status": "ok"}

@router.options("/register")
async def options_register():
    return {"status": "ok"}

@router.options("/register/admin")
async def options_register_admin():
    return {"status": "ok"}

@router.options("/promote/{usuario_id}")
async def options_promote():
    return {"status": "ok"}


# ========== ENDPOINT 1: REGISTRAR USUARIO NORMAL ==========

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn):
    """
    Registro de usuario normal:
    - Verifica que el correo no exista
    - Hashea la contraseña
    - Inserta en Supabase con rol = 'user'
    """
    existing = get_user_by_email(payload.correo)
    if existing:
        print(f"❌ Usuario ya existe: {payload.correo}")
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_pw = hash_password(payload.password)
    insert_user(
        payload.nombre, 
        payload.apellido, 
        payload.edad, 
        payload.correo, 
        hashed_pw,
        rol="user"  # Usuario normal
    )

    return {"msg": "Usuario registrado correctamente"}


# ========== ENDPOINT 2: REGISTRAR ADMIN ==========

@router.post("/register/admin", status_code=status.HTTP_201_CREATED)
def register_admin(payload: RegisterAdminIn):
    """
    Registra un nuevo admin (requiere clave secreta).
    
    Body:
    {
        "nombre": "Admin",
        "apellido": "Principal",
        "edad": 30,
        "correo": "admin@fintrack.com",
        "password": "AdminPass123!",
        "admin_key": "AdminFintrack2025!@#"
    }
    """
    # Verificar la clave de admin
    if payload.admin_key != ADMIN_KEY:
        print(f"❌ Intento de registro de admin con clave incorrecta")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de admin inválida"
        )
    
    # Verificar que el correo no exista
    existing = get_user_by_email(payload.correo)
    if existing:
        print(f"❌ Usuario ya existe: {payload.correo}")
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Hashear contraseña
    hashed_pw = hash_password(payload.password)
    
    # Insertar con rol = "admin"
    insert_user(
        payload.nombre, 
        payload.apellido, 
        payload.edad, 
        payload.correo, 
        hashed_pw,
        rol="admin"  # ← ADMIN
    )

    return {"msg": "Admin registrado correctamente"}


# ========== ENDPOINT 3: LOGIN (CON ROL) ==========

@router.post("/login")
def login(payload: LoginIn):
    """
    Login:
    - Busca usuario por correo
    - Verifica contraseña
    - Genera JWT con sub = id y rol
    """
    user = get_user_by_email(payload.correo)
    if not user:
        print(f"❌ Usuario no encontrado: {payload.correo}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(payload.password, user["password"]):
        print(f"❌ Contraseña incorrecta: {payload.correo}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Incluir rol en el token
    token = create_access_token({
        "sub": user["id"],
        "rol": user.get("rol", "user")
    })

    return {"access_token": token, "token_type": "bearer"}


# ========== ENDPOINT 4: PROMOVER USUARIO A ADMIN ==========

@router.post("/promote/{usuario_id}")
def promote_to_admin(usuario_id: str, payload: PromoteUserIn, current_admin: dict = Depends(verify_token)):
    """
    Promueve un usuario normal a admin.
    Solo los admins pueden hacer esto.
    
    Path: /auth/promote/{usuario_id}
    Body:
    {
        "admin_key": "AdminFintrack2025!@#"
    }
    Headers:
    Authorization: Bearer token_de_admin
    """
    # Verificar que quien llama sea admin
    if current_admin.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden promover usuarios"
        )
    
    # Verificar clave de admin
    if payload.admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de admin inválida"
        )
    
    # Verificar que el usuario exista
    user = get_user_by_id(usuario_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar rol a "admin"
    update_url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{usuario_id}"
    update_payload = {"rol": "admin"}
    
    update_headers = headers.copy()
    update_headers["Prefer"] = "return=representation"
    
    update_res = requests.patch(update_url, headers=update_headers, json=update_payload)
    
    if update_res.status_code not in (200, 204):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar usuario"
        )
    
    return {
        "msg": f"Usuario {usuario_id} promovido a admin correctamente",
        "usuario_id": usuario_id,
        "nuevo_rol": "admin"
    }


# ========== ENDPOINT 5: GET /me (CON ROL) ==========

@router.get("/me")
def read_users_me(payload: dict = Depends(verify_token)):
    """
    Devuelve los datos básicos del usuario autenticado incluyendo rol.
    """
    user_id = payload["sub"]

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
        "rol": user.get("rol", "user"),  # ← INCLUIR ROL
    }


# ========= RECOVER → Generar token y ENVIAR correo =======
@router.post("/recover")
def recover_password(payload: RecoverRequest):
    user = get_user_by_email(payload.correo)
    if not user:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    token = generate_recovery_token({"sub": user["id"]}, expires_minutes=10)

    # Enviar correo REAL
    send_recovery_email(user["correo"], token)

    return {"msg": "Correo enviado. Revisa tu bandeja."}


# ====== RESET → Validar token y cambiar contraseña =======
@router.post("/reset")
def reset_password(payload: ResetRequest):
    if payload.nueva_password != payload.confirmar_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    try:
        token_data = verify_recovery_token(payload.token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_id = token_data.get("sub")

    hashed = hash_password(payload.nueva_password)
    url = f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{user_id}"

    res = requests.patch(url, headers=headers, json={"password": hashed})

    if res.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Error actualizando contraseña")

    return {"msg": "Contraseña actualizada correctamente"}

# ======= CHANGE-PASSWORD → Cambiar contraseña desde el perfil ==========
@router.patch("/change-password")
def change_password(payload: ChangePasswordRequest, token_payload: dict = Depends(verify_token)):

    if payload.nueva != payload.confirmar:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    user_id = token_payload["sub"]
    user = get_user_by_id(user_id)

    if not verify_password(payload.actual, user["password"]):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    hashed = hash_password(payload.nueva)

    res = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{USERS_TABLE}?id=eq.{user_id}",
        headers=headers,
        json={"password": hashed}
    )

    if res.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Error al actualizar contraseña")

    return {"msg": "Contraseña cambiada correctamente"}
 