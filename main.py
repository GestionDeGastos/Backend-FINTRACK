from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# --- Importaciones desde src ---
from src.routes.user_routes import router as usuarios_router
from src.routes.auth_routes import router as auth_router
from src.middleware.auth_middleware import verify_token

app = FastAPI(title="API Gestión de Gastos")

# --- Configurar CORS ---
origins = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],
)

# --- Incluir routers ---
print("Registrando routers...")
app.include_router(usuarios_router)
app.include_router(auth_router)
print(" Routers registrados correctamente")

for route in app.routes:
    print(f" {route.path}")

# --- Ruta protegida de ejemplo ---
@app.get("/perfil")
async def perfil(payload: dict = Depends(verify_token)):
    return {"mensaje": "Acceso concedido a ruta protegida", "usuario": payload["sub"]}

# --- Ruta raíz ---
@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
