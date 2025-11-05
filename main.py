from fastapi import FastAPI

app = FastAPI(title="API Gestión de Gastos")

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}