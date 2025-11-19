from src.database.supabase_client import supabase

# TOTAL INGRESOS

def get_total_ingresos(user_id: str):
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

# TOTAL GASTOS

def get_total_gastos(user_id: str):
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

# GASTO PROMEDIO
def get_gasto_promedio(user_id: str):
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

# TOP CATEGORÍAS
def get_top_categorias(user_id: str, limit: int = 5):
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

# FUNCIÓN PRINCIPAL DEL DASHBOARD

def get_dashboard_data(user_id: str):
    total_ingresos = get_total_ingresos(user_id)
    total_gastos = get_total_gastos(user_id)
    gasto_promedio = get_gasto_promedio(user_id)
    ahorro_actual = total_ingresos - total_gastos
    categorias_principales = get_top_categorias(user_id)

    return {
        "summary": {
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "gasto_promedio": gasto_promedio,
            "ahorro_actual": ahorro_actual
        },
        "categorias_principales": categorias_principales
    }
