from src.database.supabase_client import supabase

# ✅ OPTIMIZADO: Solo 2 consultas a DB (ingresos y gastos), todo lo demás se calcula en memoria
def get_dashboard_data(user_id: str):
    """
    Obtiene todos los datos del dashboard con solo 2 consultas a la base de datos.
    Calcula todos los totales, promedios y categorías en memoria para máxima velocidad.
    """
    # 🚀 CONSULTA 1: Obtener TODOS los ingresos del usuario de una sola vez
    ingresos_resp = (
        supabase
        .table("ingresos")
        .select("monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    ingresos_rows = ingresos_resp.data or []
    
    # 🚀 CONSULTA 2: Obtener TODOS los gastos con categorías de una sola vez
    gastos_resp = (
        supabase
        .table("gastos")
        .select("categoria, monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    gastos_rows = gastos_resp.data or []
    
    # 💾 CÁLCULOS EN MEMORIA (super rápido)
    
    # Calcular total de ingresos
    total_ingresos = 0
    for item in ingresos_rows:
        try:
            total_ingresos += float(item["monto"])
        except:
            continue
    
    # Calcular total de gastos, promedio y categorías simultáneamente
    total_gastos = 0
    gastos_valores = []
    totales_categorias = {}
    
    for row in gastos_rows:
        try:
            monto = float(row["monto"])
            total_gastos += monto
            gastos_valores.append(monto)
            
            # Acumular por categoría
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
    
    # 📦 Retornar todo de una sola vez
    return {
        "summary": {
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "gasto_promedio": gasto_promedio,
            "ahorro_actual": ahorro_actual
        },
        "categorias_principales": categorias_principales
    }


# 🔧 Funciones auxiliares (mantener por compatibilidad, pero ya no se usan internamente)
def get_total_ingresos(user_id: str):
    """⚠️ Deprecated: Usa get_dashboard_data() para mejor rendimiento"""
    resp = (
        supabase
        .table("ingresos")
        .select("monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    rows = resp.data or []
    total = 0
    for item in rows:
        try:
            total += float(item["monto"])
        except:
            continue
    return total


def get_total_gastos(user_id: str):
    """⚠️ Deprecated: Usa get_dashboard_data() para mejor rendimiento"""
    resp = (
        supabase
        .table("gastos")
        .select("monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    rows = resp.data or []
    total = 0
    for item in rows:
        try:
            total += float(item["monto"])
        except:
            continue
    return total


def get_gasto_promedio(user_id: str):
    """⚠️ Deprecated: Usa get_dashboard_data() para mejor rendimiento"""
    resp = (
        supabase
        .table("gastos")
        .select("monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        return 0
    valores = []
    for item in rows:
        try:
            valores.append(float(item["monto"]))
        except:
            continue
    if not valores:
        return 0
    return sum(valores) / len(valores)


def get_top_categorias(user_id: str, limit: int = 5):
    """⚠️ Deprecated: Usa get_dashboard_data() para mejor rendimiento"""
    resp = (
        supabase
        .table("gastos")
        .select("categoria, monto")
        .eq("usuario_id", user_id)
        .execute()
    )
    rows = resp.data or []
    totales = {}
    for row in rows:
        categoria = row.get("categoria") or "Sin categoría"
        try:
            monto = float(row["monto"])
        except:
            monto = 0
        totales[categoria] = totales.get(categoria, 0) + monto
    sorted_items = sorted(totales.items(), key=lambda x: x[1], reverse=True)
    top = sorted_items[:limit]
    return {
        "labels": [name for name, _ in top],
        "values": [amount for _, amount in top]
    }
