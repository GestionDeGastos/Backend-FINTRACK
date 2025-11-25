# main.py (versión limpia sin ruta de prueba)
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

bearer_scheme = HTTPBearer()

from src.routes.user_routes import router as usuarios_router
from src.routes.auth_routes import router as auth_router
from src.routes.ingresos_routes import router as ingresos_router
from src.routes.gastos_routes import router as gastos_router
from src.middleware.auth_middleware import verify_token
from src.routes.plan_gestion_routes import router as plan_gestion_router
from src.routes.perfil_routes import router as perfil_router
from src.routes.gasto_extra_routes import router as gastos_extra_router
from fastapi.staticfiles import StaticFiles

#DASHBOARD
from src.routes.dashboard_routes import router as dashboard_router
from src.routes.admin_routes import router as admin_router


app = FastAPI(title="API Gestión de Gastos")

# --- Configurar CORS ---
origins = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

print("📦 Registrando routers...")
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(ingresos_router)
app.include_router(gastos_router)
app.include_router(plan_gestion_router)
app.include_router(perfil_router)
app.include_router(gastos_extra_router)

app.include_router(dashboard_router)
app.include_router(admin_router)

print("✅ Routers registrados correctamente")
for route in app.routes:
    print(f"🔹 {route.path}")

# 🚫 ELIMINAMOS ESTA RUTA
# @app.get("/")
# def root():
#     return {"message": "API funcionando correctamente"}

# ---------------------------------------------------------
# 💥 AQUI VA EL MOUNT DEL FRONTEND  (AL FINAL DEL ARCHIVO)
# ---------------------------------------------------------
app.mount(
    "/",
    StaticFiles(directory="../Frontend-GestionGastos", html=True),
    name="frontend"
)
