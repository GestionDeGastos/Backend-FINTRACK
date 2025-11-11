
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# --- Importaciones de rutas desde src ---
from src.routes.user_routes import router as usuarios_router
from src.routes.auth_routes import router as auth_router
from src.routes.ingresos_routes import router as ingresos_router
from src.routes.gastos_routes import router as gastos_router
from src.routes.plan_ahorro_routes import router as plan_ahorro_router
from src.routes.report_routes import router as report_router
from src.routes.plan_gestion_routes import router as plan_gestion_router  # 👈 NUEVO

# --- Middleware de autenticación ---
from src.middleware.auth_middleware import verify_token

app = FastAPI(title="API Gestión de Gastos", version="2.0.0")

origins = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
    "http://localhost:3000",   # 👈 agrega aquí tu frontend si usas React, Next.js, etc.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],          # Permitir todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],          # Permitir todos los encabezados
)

print("📦 Registrando routers...")

app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(ingresos_router)
app.include_router(gastos_router)
app.include_router(plan_ahorro_router)
app.include_router(report_router)
app.include_router(plan_gestion_router)  # 👈 Nuevo módulo: Plan de Gestión de Gastos

print("✅ Routers registrados correctamente")

# Mostrar rutas registradas en consola
for route in app.routes:
    print(f"🔹 {route.path}")

@app.get("/perfil")
async def perfil(payload: dict = Depends(verify_token)):
    """
    Ejemplo de ruta protegida con middleware de autenticación.
    Devuelve el usuario actual basado en su token JWT.
    """
    return {
        "mensaje": "Acceso concedido a ruta protegida",
        "usuario": payload["sub"]
    }

@app.get("/")
def root():
    """
    Endpoint principal para verificar el estado de la API.
    """
    return {"message": "✅ API funcionando correctamente"}

