from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date
from src.schemas.report_schemas import ReporteRangoResp, Periodo
from src.services.report_service import calcular_reporte_rango
from src.middleware.auth_middleware import verify_token

router = APIRouter(prefix="/api", tags=["reportes"])

@router.get("/reporte", response_model=ReporteRangoResp)
def reporte_por_rango(
    inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    payload: dict = Depends(verify_token)
):
    """
    Retorna los totales de ingresos, gastos y ahorro del usuario
    en el rango de fechas especificado.
    """
    if fin < inicio:
        raise HTTPException(status_code=400, detail="La fecha fin no puede ser menor que la fecha inicio.")

    try:
        usuario_id = payload.get("sub")
        data = calcular_reporte_rango(usuario_id, inicio, fin)

        return ReporteRangoResp(
            periodo=Periodo(inicio=inicio, fin=fin),
            total_ingresos=data["total_ingresos"],
            total_gastos=data["total_gastos"],
            total_ahorro=data["total_ahorro"],
            balance=data["balance"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {e}")
