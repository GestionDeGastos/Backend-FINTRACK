from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

bearer_scheme = HTTPBearer()

# --- Importaciones desde src ---
from src.routes.user_routes import router as usuarios_router
from src.routes.auth_routes import router as auth_router
from src.routes.ingresos_routes import router as ingresos_router
from src.routes.gastos_routes import router as gastos_router
from src.middleware.auth_middleware import verify_token
from src.routes.plan_gestion_routes import router as plan_gestion_router

app = FastAPI(title="API Gestión de Gastos")

# --- CORS MEJORADO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "*",  # Temporalmente para desarrollo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# --- Incluir routers ---
print("📦 Registrando routers...")
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(ingresos_router)
app.include_router(gastos_router)
app.include_router(plan_gestion_router)

print("✅ Routers registrados correctamente")

for route in app.routes:
    print(f"🔹 {route.path}")

# --- Ruta protegida de ejemplo ---
@app.get("/perfil")
async def perfil(payload: dict = Depends(verify_token)):
    return {"mensaje": "Acceso concedido a ruta protegida", "usuario": payload["sub"]}

# --- Ruta raíz ---
@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}