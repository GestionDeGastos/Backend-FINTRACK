from fastapi import APIRouter, Depends, HTTPException, status
from src.middleware.auth_middleware import verify_token
from src.services.admin_dashboard_service import (
    get_dashboard_admin,
    get_lista_usuarios_con_stats,
    get_estadisticas_usuario_admin
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)


def validar_admin(token: str = Depends(verify_token)):
    """Validar que el usuario sea admin"""
    if token.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a esta sección"
        )
    return token


# ===== DASHBOARD ADMIN =====

@router.get("/dashboard")
def get_dashboard(admin: dict = Depends(validar_admin)):
    """
    Obtener dashboard administrativo con métricas globales
    
    Retorna:
    - Total usuarios
    - Ingresos totales del sistema
    - Gastos totales
    - Gastos extraordinarios totales
    - Planes creados
    - Promedios generales
    - Top categorías más gastadas
    """
    try:
        dashboard = get_dashboard_admin()
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener dashboard administrativo: {str(e)}"
        )


# ===== LISTA DE USUARIOS =====

@router.get("/usuarios")
def get_usuarios(admin: dict = Depends(validar_admin)):
    """
    Obtener lista de todos los usuarios con sus estadísticas
    
    Retorna lista de usuarios ordenada por ingresos (de mayor a menor)
    con: nombre, email, total_ingresos, total_gastos, ahorro, planes_activos, fecha_registro
    """
    try:
        usuarios = get_lista_usuarios_con_stats()
        return {
            "total_usuarios": len(usuarios),
            "usuarios": usuarios
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


# ===== ESTADÍSTICAS DE UN USUARIO =====

@router.get("/usuario/{usuario_id}")
def get_estadisticas_usuario(
    usuario_id: str,
    admin: dict = Depends(validar_admin)
):
    """
    Obtener estadísticas completas de un usuario específico
    
    Retorna:
    - Datos personales
    - Total ingresos, gastos, ahorro
    - Gasto promedio
    - Distribución de gastos por categoría
    - Planes activos
    - Gastos extraordinarios recientes
    """
    try:
        estadisticas = get_estadisticas_usuario_admin(usuario_id)
        return estadisticas
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )