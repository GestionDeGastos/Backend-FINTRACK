from src.database.supabase_client import supabase
from collections import defaultdict

# ✅ OPTIMIZADO: Dashboard administrativo con mínimas consultas a DB

def get_dashboard_admin():
    """
    Obtener dashboard administrativo con métricas globales.
    ✨ OPTIMIZADO: Solo 4 consultas a DB en lugar de múltiples por usuario.
    """
    try:
        # 🚀 CONSULTA 1: Todos los usuarios
        usuarios_resp = supabase.table("usuarios").select("id").execute()
        usuarios = usuarios_resp.data or []
        total_usuarios = len(usuarios)
        
        # 🚀 CONSULTA 2: Todos los ingresos del sistema
        ingresos_resp = supabase.table("ingresos").select("monto").execute()
        ingresos_rows = ingresos_resp.data or []
        
        # 🚀 CONSULTA 3: Todos los gastos del sistema con categorías
        gastos_resp = supabase.table("gastos").select("categoria, monto").execute()
        gastos_rows = gastos_resp.data or []
        
        # 🚀 CONSULTA 4: Todos los planes
        planes_resp = supabase.table("plan_gestion").select("id").execute()
        planes_creados = len(planes_resp.data or [])
        
        # 🚀 CONSULTA 5: Todos los gastos extraordinarios (columna extraordinario=true)
        gastos_extra_resp = supabase.table("gastos").select("monto").eq("extraordinario", True).execute()
        gastos_extra_rows = gastos_extra_resp.data or []
        
        # 💾 CÁLCULOS EN MEMORIA
        
        # Calcular ingresos totales
        ingresos_totales = 0
        for item in ingresos_rows:
            try:
                ingresos_totales += float(item.get("monto", 0))
            except:
                continue
        
        # Calcular gastos totales y categorías simultáneamente
        gastos_totales = 0
        totales_categorias = {}
        
        for row in gastos_rows:
            try:
                monto = float(row.get("monto", 0))
                gastos_totales += monto
                
                categoria = row.get("categoria") or "Sin categoría"
                totales_categorias[categoria] = totales_categorias.get(categoria, 0) + monto
            except:
                continue
        
        # Calcular gastos extraordinarios totales
        gastos_extraordinarios = 0
        for item in gastos_extra_rows:
            try:
                gastos_extraordinarios += float(item.get("monto", 0))
            except:
                continue
        
        # Calcular promedios
        promedio_ingresos_por_usuario = ingresos_totales / total_usuarios if total_usuarios > 0 else 0
        promedio_gastos_por_usuario = gastos_totales / total_usuarios if total_usuarios > 0 else 0
        ahorro_promedio = promedio_ingresos_por_usuario - promedio_gastos_por_usuario
        
        # Top 5 categorías
        sorted_categorias = sorted(totales_categorias.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_categorias[:5]
        
        top_categorias = {
            "labels": [nombre for nombre, _ in top_5],
            "values": [monto for _, monto in top_5],
            "count": len(top_5)
        }
        
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


def get_lista_usuarios_con_stats():
    """
    Obtener lista de todos los usuarios con sus estadísticas.
    ✨ OPTIMIZADO: Solo 4 consultas a DB en lugar de 3*N consultas (N = número de usuarios).
    """
    try:
        # 🚀 CONSULTA 1: Todos los usuarios
        usuarios_resp = supabase.table("usuarios").select("*").execute()
        usuarios = usuarios_resp.data or []
        
        # 🚀 CONSULTA 2: Todos los ingresos (agrupamos por usuario_id en memoria)
        ingresos_resp = supabase.table("ingresos").select("usuario_id, monto").execute()
        ingresos_rows = ingresos_resp.data or []
        
        # 🚀 CONSULTA 3: Todos los gastos (agrupamos por usuario_id en memoria)
        gastos_resp = supabase.table("gastos").select("usuario_id, monto").execute()
        gastos_rows = gastos_resp.data or []
        
        # 🚀 CONSULTA 4: Todos los planes (agrupamos por usuario_id en memoria)
        planes_resp = supabase.table("plan_gestion").select("usuario_id, id").execute()
        planes_rows = planes_resp.data or []
        
        # 💾 AGRUPAR DATOS POR USUARIO EN MEMORIA
        ingresos_por_usuario = defaultdict(float)
        for item in ingresos_rows:
            try:
                user_id = item.get("usuario_id")
                monto = float(item.get("monto", 0))
                ingresos_por_usuario[user_id] += monto
            except:
                continue
        
        gastos_por_usuario = defaultdict(float)
        for item in gastos_rows:
            try:
                user_id = item.get("usuario_id")
                monto = float(item.get("monto", 0))
                gastos_por_usuario[user_id] += monto
            except:
                continue
        
        planes_por_usuario = defaultdict(int)
        for item in planes_rows:
            user_id = item.get("usuario_id")
            if user_id:
                planes_por_usuario[user_id] += 1
        
        # 📦 CONSTRUIR LISTA DE USUARIOS CON SUS STATS
        lista_usuarios = []
        for usuario in usuarios:
            user_id = usuario.get("id")
            total_ingresos = ingresos_por_usuario.get(user_id, 0)
            total_gastos = gastos_por_usuario.get(user_id, 0)
            ahorro = total_ingresos - total_gastos
            planes_activos = planes_por_usuario.get(user_id, 0)
            
            lista_usuarios.append({
                "id": user_id,
                "nombre": usuario.get("nombre", "Sin nombre"),
                "email": usuario.get("correo") or usuario.get("email", "Sin email"),
                "edad": usuario.get("edad", 0),
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


def get_estadisticas_usuario_admin(user_id: str):
    """
    Obtener estadísticas completas de un usuario específico (para admin).
    ✨ OPTIMIZADO: Solo 5 consultas a DB en lugar de 7.
    """
    try:
        # 🚀 CONSULTA 1: Datos del usuario
        usuario_resp = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        usuario = usuario_resp.data[0] if usuario_resp.data else None
        
        if not usuario:
            raise ValueError(f"Usuario {user_id} no encontrado")
        
        # 🚀 CONSULTA 2: Ingresos del usuario
        ingresos_resp = supabase.table("ingresos").select("monto").eq("usuario_id", user_id).execute()
        ingresos_rows = ingresos_resp.data or []
        
        # 🚀 CONSULTA 3: Gastos del usuario con categorías
        gastos_resp = supabase.table("gastos").select("categoria, monto").eq("usuario_id", user_id).execute()
        gastos_rows = gastos_resp.data or []
        
        # 🚀 CONSULTA 4: Planes del usuario
        planes_resp = supabase.table("plan_gestion").select("id").eq("usuario_id", user_id).execute()
        planes_activos = len(planes_resp.data or [])
        
        # 🚀 CONSULTA 5: Gastos extraordinarios recientes (columna extraordinario=true)
        gastos_extra_resp = (
            supabase
            .table("gastos")
            .select("id, nombre_gasto, monto, fecha, categoria")
            .eq("usuario_id", user_id)
            .eq("extraordinario", True)
            .order("fecha", desc=True)
            .limit(5)
            .execute()
        )
        
        # 💾 CÁLCULOS EN MEMORIA
        
        # Calcular total de ingresos
        total_ingresos = 0
        for item in ingresos_rows:
            try:
                total_ingresos += float(item.get("monto", 0))
            except:
                continue
        
        # Calcular total de gastos, promedio y categorías
        total_gastos = 0
        gastos_valores = []
        totales_categorias = {}
        
        for row in gastos_rows:
            try:
                monto = float(row.get("monto", 0))
                total_gastos += monto
                gastos_valores.append(monto)
                
                categoria = row.get("categoria") or "Sin categoría"
                totales_categorias[categoria] = totales_categorias.get(categoria, 0) + monto
            except:
                continue
        
        # Calcular gasto promedio
        gasto_promedio = sum(gastos_valores) / len(gastos_valores) if gastos_valores else 0
        
        # Calcular ahorro
        ahorro_actual = total_ingresos - total_gastos
        
        # Top 5 categorías
        sorted_categorias = sorted(totales_categorias.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_categorias[:5]
        
        categorias_principales = {
            "labels": [nombre for nombre, _ in top_5],
            "values": [monto for _, monto in top_5]
        }
        
        # Procesar gastos extraordinarios
        gastos_extraordinarios_recientes = [
            {
                "id": g.get("id"),
                "descripcion": g.get("nombre_gasto"),  # nombre_gasto en lugar de descripcion
                "monto": round(float(g.get("monto", 0)), 2),
                "fecha": g.get("fecha"),
                "categoria": g.get("categoria")
            }
            for g in (gastos_extra_resp.data or [])
        ]
        
        return {
            "usuario_id": user_id,
            "nombre": usuario.get("nombre"),
            "email": usuario.get("correo") or usuario.get("email"),
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


# 🔧 Funciones auxiliares (mantener por compatibilidad, pero ya no se usan internamente)

def get_total_usuarios():
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
    try:
        resp = supabase.table("usuarios").select("id").execute()
        return len(resp.data or [])
    except Exception as e:
        print(f"Error obteniendo total de usuarios: {e}")
        return 0


def get_ingresos_totales_sistema():
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
    try:
        resp = supabase.table("plan_gestion").select("id").execute()
        return len(resp.data or [])
    except Exception as e:
        print(f"Error obteniendo planes: {e}")
        return 0


def get_gastos_extraordinarios_totales():
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
    try:
        resp = supabase.table("gastos").select("monto").eq("extraordinario", True).execute()
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
    """⚠️ Deprecated: Usa get_dashboard_admin() para mejor rendimiento"""
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


def get_total_ingresos_usuario(user_id: str):
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
    try:
        resp = supabase.table("plan_gestion").select("id").eq("usuario_id", user_id).execute()
        return len(resp.data or [])
    except:
        return 0


def get_gasto_promedio_usuario(user_id: str):
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
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
    """⚠️ Deprecated: Usa get_estadisticas_usuario_admin() para mejor rendimiento"""
    try:
        resp = (
            supabase
            .table("gastos") 
            .select("id, nombre_gasto, monto, fecha, categoria")
            .eq("usuario_id", user_id)
            .eq("extraordinario", True)
            .order("fecha", desc=True)
            .limit(limit)
            .execute()
        )
        gastos = resp.data or []
        return [
            {
                "id": g.get("id"),
                "descripcion": g.get("nombre_gasto"),
                "monto": round(float(g.get("monto", 0)), 2),
                "fecha": g.get("fecha"),
                "categoria": g.get("categoria")
            }
            for g in gastos
        ]
    except:
        return []