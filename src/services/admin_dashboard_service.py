from src.database.supabase_client import supabase

# ===== MÉTRICAS GLOBALES =====

def get_total_usuarios():
    """Obtener total de usuarios en el sistema"""
    try:
        resp = supabase.table("usuarios").select("id").execute()
        return len(resp.data or [])
    except Exception as e:
        print(f"Error obteniendo total de usuarios: {e}")
        return 0


def get_ingresos_totales_sistema():
    """Obtener ingresos totales de todos los usuarios"""
    try:
        resp = supabase.table("ingresos").select("monto").execute()
        rows = resp.data or []
        
        total = 0
        for item in rows:
            try:
                total += float(item.get("monto", 0))
            except:
                continue
        
        return total
    except Exception as e:
        print(f"Error obteniendo ingresos totales: {e}")
        return 0


def get_gastos_totales_sistema():
    """Obtener gastos totales de todos los usuarios"""
    try:
        resp = supabase.table("gastos").select("monto").execute()
        rows = resp.data or []
        
        total = 0
        for item in rows:
            try:
                total += float(item.get("monto", 0))
            except:
                continue
        
        return total
    except Exception as e:
        print(f"Error obteniendo gastos totales: {e}")
        return 0


def get_planes_creados():
    """Obtener total de planes creados en el sistema"""
    try:
        resp = supabase.table("planes").select("id").execute()
        return len(resp.data or [])
    except Exception as e:
        print(f"Error obteniendo planes: {e}")
        return 0


def get_gastos_extraordinarios_totales():
    """Obtener total de gastos extraordinarios"""
    try:
        resp = supabase.table("gastos_extraordinarios").select("monto").execute()
        rows = resp.data or []
        
        total = 0
        for item in rows:
            try:
                total += float(item.get("monto", 0))
            except:
                continue
        
        return total
    except Exception as e:
        print(f"Error obteniendo gastos extraordinarios: {e}")
        return 0


def get_top_categorias_sistema(limit: int = 5):
    """Obtener top categorías más gastadas en todo el sistema"""
    try:
        resp = supabase.table("gastos").select("categoria, monto").execute()
        
        rows = resp.data or []
        totales = {}
        
        for row in rows:
            categoria = row.get("categoria") or "Sin categoría"
            try:
                monto = float(row.get("monto", 0))
            except:
                monto = 0
            
            totales[categoria] = totales.get(categoria, 0) + monto
        
        sorted_items = sorted(totales.items(), key=lambda x: x[1], reverse=True)
        top = sorted_items[:limit]
        
        return {
            "labels": [name for name, _ in top],
            "values": [amount for _, amount in top],
            "count": len(top)
        }
    except Exception as e:
        print(f"Error obteniendo top categorías: {e}")
        return {"labels": [], "values": [], "count": 0}


def get_dashboard_admin():
    """Obtener dashboard administrativo con métricas globales"""
    try:
        total_usuarios = get_total_usuarios()
        ingresos_totales = get_ingresos_totales_sistema()
        gastos_totales = get_gastos_totales_sistema()
        planes_creados = get_planes_creados()
        gastos_extraordinarios = get_gastos_extraordinarios_totales()
        top_categorias = get_top_categorias_sistema()
        
        promedio_ingresos_por_usuario = ingresos_totales / total_usuarios if total_usuarios > 0 else 0
        promedio_gastos_por_usuario = gastos_totales / total_usuarios if total_usuarios > 0 else 0
        ahorro_promedio = promedio_ingresos_por_usuario - promedio_gastos_por_usuario
        
        return {
            "metricas_globales": {
                "total_usuarios": total_usuarios,
                "ingresos_totales_sistema": round(ingresos_totales, 2),
                "gastos_totales_sistema": round(gastos_totales, 2),
                "gastos_extraordinarios_totales": round(gastos_extraordinarios, 2),
                "planes_creados": planes_creados,
                "promedio_ingresos_por_usuario": round(promedio_ingresos_por_usuario, 2),
                "promedio_gastos_por_usuario": round(promedio_gastos_por_usuario, 2),
                "ahorro_promedio": round(ahorro_promedio, 2)
            },
            "top_categorias": top_categorias,
            "total_categorias": top_categorias.get("count", 0)
        }
    except Exception as e:
        print(f"Error en get_dashboard_admin: {e}")
        return {
            "metricas_globales": {},
            "top_categorias": {"labels": [], "values": []},
            "total_categorias": 0
        }


# ===== LISTA DE USUARIOS CON ESTADÍSTICAS =====

def get_total_ingresos_usuario(user_id: str):
    """Obtener total de ingresos de un usuario"""
    try:
        resp = supabase.table("ingresos").select("monto").eq("usuario_id", user_id).execute()
        rows = resp.data or []
        
        total = 0
        for item in rows:
            try:
                total += float(item.get("monto", 0))
            except:
                continue
        
        return total
    except:
        return 0


def get_total_gastos_usuario(user_id: str):
    """Obtener total de gastos de un usuario"""
    try:
        resp = supabase.table("gastos").select("monto").eq("usuario_id", user_id).execute()
        rows = resp.data or []
        
        total = 0
        for item in rows:
            try:
                total += float(item.get("monto", 0))
            except:
                continue
        
        return total
    except:
        return 0


def get_planes_activos_usuario(user_id: str):
    """Obtener cantidad de planes activos de un usuario"""
    try:
        resp = supabase.table("planes").select("id").eq("usuario_id", user_id).eq("activo", True).execute()
        return len(resp.data or [])
    except:
        return 0


def get_lista_usuarios_con_stats():
    """Obtener lista de todos los usuarios con sus estadísticas"""
    try:
        usuarios_resp = supabase.table("usuarios").select("*").execute()
        usuarios = usuarios_resp.data or []
        
        lista_usuarios = []
        
        for usuario in usuarios:
            user_id = usuario.get("id")
            total_ingresos = get_total_ingresos_usuario(user_id)
            total_gastos = get_total_gastos_usuario(user_id)
            ahorro = total_ingresos - total_gastos
            planes_activos = get_planes_activos_usuario(user_id)
            
            lista_usuarios.append({
                "id": user_id,
                "nombre": usuario.get("nombre", "Sin nombre"),
                "email": usuario.get("email", "Sin email"),
                "total_ingresos": round(total_ingresos, 2),
                "total_gastos": round(total_gastos, 2),
                "ahorro": round(ahorro, 2),
                "planes_activos": planes_activos,
                "fecha_registro": usuario.get("created_at", "")
            })
        
        return sorted(lista_usuarios, key=lambda x: x["total_ingresos"], reverse=True)
    except Exception as e:
        print(f"Error en get_lista_usuarios_con_stats: {e}")
        return []


# ===== ESTADÍSTICAS DETALLADAS DE UN USUARIO =====

def get_gasto_promedio_usuario(user_id: str):
    """Obtener gasto promedio de un usuario"""
    try:
        resp = supabase.table("gastos").select("monto").eq("usuario_id", user_id).execute()
        rows = resp.data or []
        
        if not rows:
            return 0
        
        valores = []
        for item in rows:
            try:
                valores.append(float(item.get("monto", 0)))
            except:
                continue
        
        if not valores:
            return 0
        
        return sum(valores) / len(valores)
    except:
        return 0


def get_categorias_usuario(user_id: str, limit: int = 5):
    """Obtener categorías de gastos de un usuario"""
    try:
        resp = supabase.table("gastos").select("categoria, monto").eq("usuario_id", user_id).execute()
        
        rows = resp.data or []
        totales = {}
        
        for row in rows:
            categoria = row.get("categoria") or "Sin categoría"
            try:
                monto = float(row.get("monto", 0))
            except:
                monto = 0
            
            totales[categoria] = totales.get(categoria, 0) + monto
        
        sorted_items = sorted(totales.items(), key=lambda x: x[1], reverse=True)
        top = sorted_items[:limit]
        
        return {
            "labels": [name for name, _ in top],
            "values": [amount for _, amount in top]
        }
    except:
        return {"labels": [], "values": []}


def get_gastos_extraordinarios_usuario(user_id: str, limit: int = 5):
    """Obtener gastos extraordinarios recientes de un usuario"""
    try:
        resp = (
            supabase
            .table("gastos_extraordinarios")
            .select("*")
            .eq("usuario_id", user_id)
            .order("fecha", desc=True)
            .limit(limit)
            .execute()
        )
        
        gastos = resp.data or []
        return [
            {
                "id": g.get("id"),
                "descripcion": g.get("descripcion"),
                "monto": round(float(g.get("monto", 0)), 2),
                "fecha": g.get("fecha"),
                "categoria": g.get("categoria")
            }
            for g in gastos
        ]
    except:
        return []


def get_estadisticas_usuario_admin(user_id: str):
    """Obtener estadísticas completas de un usuario específico (para admin)"""
    try:
        # Obtener datos del usuario
        usuario_resp = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        usuario = usuario_resp.data[0] if usuario_resp.data else None
        
        if not usuario:
            raise ValueError(f"Usuario {user_id} no encontrado")
        
        total_ingresos = get_total_ingresos_usuario(user_id)
        total_gastos = get_total_gastos_usuario(user_id)
        gasto_promedio = get_gasto_promedio_usuario(user_id)
        ahorro_actual = total_ingresos - total_gastos
        categorias_principales = get_categorias_usuario(user_id)
        
        # Planes activos
        planes_activos = get_planes_activos_usuario(user_id)
        
        # Gastos extraordinarios recientes
        gastos_extraordinarios_recientes = get_gastos_extraordinarios_usuario(user_id)
        
        return {
            "usuario_id": user_id,
            "nombre": usuario.get("nombre"),
            "email": usuario.get("email"),
            "fecha_registro": usuario.get("created_at"),
            "total_ingresos": round(total_ingresos, 2),
            "total_gastos": round(total_gastos, 2),
            "gasto_promedio": round(gasto_promedio, 2),
            "ahorro_actual": round(ahorro_actual, 2),
            "categorias_principales": categorias_principales,
            "planes_activos": planes_activos,
            "gastos_extraordinarios_recientes": gastos_extraordinarios_recientes
        }
    except Exception as e:
        print(f"Error en get_estadisticas_usuario_admin: {e}")
        raise