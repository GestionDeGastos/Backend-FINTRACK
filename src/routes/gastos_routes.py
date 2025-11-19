from fastapi import APIRouter, HTTPException, Depends
from src.database.supabase_client import supabase
from src.models.gastos_model import Gasto, GastoUpdate
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/gastos", tags=["gastos"])

# ----------------------------------------------------
# Crear gasto
# ----------------------------------------------------
@router.post("/", status_code=201)
def crear_gasto(gasto: Gasto, payload: dict = Depends(verify_token)):
    """
    Crea un gasto usando el UUID del usuario que viene del token.
    YA NO buscamos al usuario por correo.
    """
    usuario_id = payload["sub"]  # UUID real

    data = {
        "usuario_id": usuario_id,
        "categoria": gasto.categoria,
        "nombre_gasto": gasto.nombre_gasto,
        "monto": gasto.monto,
        "fecha": gasto.fecha,
        "descripcion": gasto.descripcion,
        "plan_id": gasto.plan_id,
        "extraordinario": gasto.extraordinario,
    }

    result = supabase.table("gastos").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="No se pudo crear el gasto")

    return {
        "message": "Gasto creado con éxito",
        "data": result.data[0],
    }


# ----------------------------------------------------
# Obtener todos los gastos del usuario
# ----------------------------------------------------
@router.get("/")
def obtener_gastos(payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("gastos")
        .select("*")
        .eq("usuario_id", usuario_id)
        .execute()
    )

    return {
        "message": "Gastos obtenidos",
        "data": result.data,
    }


# ----------------------------------------------------
# Obtener un gasto específico por ID
# ----------------------------------------------------
@router.get("/{id}")
def obtener_gasto(id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("gastos")
        .select("*")
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    return {
        "message": "Gasto encontrado",
        "data": result.data[0],
    }


# ----------------------------------------------------
# Actualizar gasto
# ----------------------------------------------------
@router.put("/{id}")
def actualizar_gasto(id: str, gasto: GastoUpdate, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    update_data = {k: v for k, v in gasto.dict().items() if v is not None}

    result = (
        supabase.table("gastos")
        .update(update_data)
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    return {
        "message": "Gasto actualizado con éxito",
        "data": result.data[0],
    }


# ----------------------------------------------------
# Eliminar gasto
# ----------------------------------------------------
@router.delete("/{id}")
def eliminar_gasto(id: str, payload: dict = Depends(verify_token)):
    usuario_id = payload["sub"]

    result = (
        supabase.table("gastos")
        .delete()
        .eq("id", id)
        .eq("usuario_id", usuario_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    return {
        "message": "Gasto eliminado con éxito",
        "id": id,
    }
