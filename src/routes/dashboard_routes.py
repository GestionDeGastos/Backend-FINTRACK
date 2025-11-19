from fastapi import APIRouter, Depends
from src.services.dashboard_service import get_dashboard_data
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def obtener_dashboard(payload: dict = Depends(verify_token)):
    """
    Devuelve datos del dashboard del usuario autenticado.
    """
    user_id = payload["sub"]   # ID del usuario desde el token
    return get_dashboard_data(user_id)
