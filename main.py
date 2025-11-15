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

app = FastAPI(title="API Gestión de Gastos - Sprint 3")

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

print("✅ Routers registrados correctamente")

for route in app.routes:
    print(f"🔹 {route.path}")

@app.get("/")
def root():
    return {"message": "API funcionando correctamente - Sprint 3"}