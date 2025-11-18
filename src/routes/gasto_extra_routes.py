from fastapi import APIRouter, HTTPException, Depends
from src.schemas.gasto_extra_schema import GastoExtraCreate
from src.services.gasto_extra_service import agregar_gasto_extra
from src.middleware.auth_middleware import verify_token  

router = APIRouter(prefix="/gastos", tags=["gastos"])

@router.post("/extraordinario", status_code=201)
def crear_gasto_extraordinario(payload: GastoExtraCreate, token_payload: dict = Depends(verify_token)):
    """
    Crea un gasto extraordinario y actualiza el saldo del plan.
    Requiere que el token contenga el identificador del usuario en 'sub' (correo o id según tu JWT).
    """
    try:
        usuario_sub = token_payload.get("sub")
        # Si tu token usa el correo, puedes obtener usuario_id en DB si lo necesitas.
        # Asumimos que plan_gestion.usuario_id coincide con token.sub (si usas id uuid aquí, debe ser id).
        result = agregar_gasto_extra(payload.plan_id, usuario_sub, payload.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
