from src.database.supabase_client import supabase
from datetime import date
from typing import List, Optional, Dict, Any

TABLE_NAME = "plan_gestion"

# --------------------------------------------
# Crear un nuevo plan de gestión
# --------------------------------------------
def crear_plan(usuario_id: str, data: dict):
    """
    Crea un nuevo plan de gestión de gasto asociado al usuario autenticado.
    """
    from datetime import date

    # Convertir fechas a string para que Supabase las acepte
    if isinstance(data.get("fecha_inicio"), date):
        data["fecha_inicio"] = data["fecha_inicio"].isoformat()
    if isinstance(data.get("fecha_fin"), date):
        data["fecha_fin"] = data["fecha_fin"].isoformat()

    # Agregar el ID del usuario autenticado
    data["usuario_id"] = usuario_id

    try:
        result = supabase.table("plan_gestion").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print("❌ Error al crear el plan de gestión:", e)
        return None



# --------------------------------------------
# Obtener todos los planes del usuario
# --------------------------------------------
def obtener_planes(usuario_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve todos los planes de gestión creados por el usuario.
    """
    try:
        result = (
            supabase.table(TABLE_NAME)
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("fecha_inicio", desc=False)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print("Error al obtener los planes de gestión:", e)
        return []


# --------------------------------------------
# Obtener un plan específico por ID
# --------------------------------------------
def obtener_plan_por_id(plan_id: int, usuario_id: str) -> Optional[Dict[str, Any]]:
    """
    Devuelve un solo plan de gestión si pertenece al usuario.
    """
    try:
        result = (
            supabase.table(TABLE_NAME)
            .select("*")
            .eq("id", plan_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print("Error al obtener plan por ID:", e)
        return None


# --------------------------------------------
# Actualizar un plan de gestión existente
# --------------------------------------------
def actualizar_plan(plan_id: int, usuario_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Actualiza un plan de gestión existente si pertenece al usuario autenticado.
    """
    try:
        result = (
            supabase.table(TABLE_NAME)
            .update(data)
            .eq("id", plan_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(" Error al actualizar el plan de gestión:", e)
        return None


# --------------------------------------------
# Eliminar un plan de gestión
# --------------------------------------------
def eliminar_plan(plan_id: int, usuario_id: str) -> bool:
    """
    Elimina un plan de gestión si pertenece al usuario.
    """
    try:
        result = (
            supabase.table(TABLE_NAME)
            .delete()
            .eq("id", plan_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(result.data)
    except Exception as e:
        print("Error al eliminar el plan de gestión:", e)
        return False
