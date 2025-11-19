from fastapi import APIRouter, HTTPException, Depends
from src.database.supabase_client import supabase
from src.models.ingresos_model import Ingreso, IngresoUpdate
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/ingresos", tags=["ingresos"])

# ----------------------------------------------------------
# CREAR INGRESO
# ----------------------------------------------------------
@router.post("/", status_code=201)
def crear_ingreso(ingreso: Ingreso, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    data = {
        "usuario_id": usuario_id,
        "concepto": ingreso.concepto,
        "nombre_fuente": ingreso.nombre_fuente,
        "monto": ingreso.monto,
        "fecha": ingreso.fecha,
        "descripcion": ingreso.descripcion
    }

    result = supabase.table("ingresos").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="No se pudo crear el ingreso")

    return {
        "message": "Ingreso creado con éxito",
        "data": result.data[0]
    }


# ----------------------------------------------------------
# OBTENER TODOS LOS INGRESOS DEL USUARIO
# ----------------------------------------------------------
@router.get("/")
def obtener_ingresos(payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("ingresos")
        .select("*")
        .eq("usuario_id", usuario_id)
        .execute()
    )

    return {
        "message": "Ingresos obtenidos",
        "data": result.data
    }


# ----------------------------------------------------------
# OBTENER INGRESO POR ID
# ----------------------------------------------------------
@router.get("/{id}")
def obtener_ingreso(id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("ingresos")
        .select("*")
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    return {
        "message": "Ingreso encontrado",
        "data": result.data[0]
    }


# ----------------------------------------------------------
# ACTUALIZAR INGRESO
# ----------------------------------------------------------
@router.put("/{id}")
def actualizar_ingreso(id: str, ingreso: IngresoUpdate, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    update_data = {k: v for k, v in ingreso.dict().items() if v is not None}

    result = (
        supabase.table("ingresos")
        .update(update_data)
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    return {
        "message": "Ingreso actualizado con éxito",
        "data": result.data[0]
    }


# ----------------------------------------------------------
# ELIMINAR INGRESO
# ----------------------------------------------------------
@router.delete("/{id}")
def eliminar_ingreso(id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("ingresos")
        .delete()
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    return {
        "message": "Ingreso eliminado con éxito",
        "id": id
    }
