from datetime import date
from src.database.supabase_client import supabase

INGRESOS_TABLE = "ingresos"
GASTOS_TABLE = "gastos"

# ✅ OPTIMIZADO: Solo 2 consultas a DB con filtros de fecha
def calcular_reporte_rango(usuario_id: str, inicio: date, fin: date) -> dict:
    """
    Calcula los totales de ingresos, gastos, ahorro y balance en el rango de fechas dado.
    ✨ OPTIMIZADO: Solo 2 consultas a DB en lugar de consultas separadas.
    """
    # 🚀 CONSULTA 1: Obtener TODOS los ingresos del usuario en el rango de fechas
    ingresos_query = (
        supabase.table(INGRESOS_TABLE)
        .select("monto, fecha")
        .eq("usuario_id", usuario_id)
        .gte("fecha", str(inicio))
        .lte("fecha", str(fin))
    )
    ingresos_data = ingresos_query.execute().data or []
    
    # 🚀 CONSULTA 2: Obtener TODOS los gastos del usuario en el rango de fechas
    gastos_query = (
        supabase.table(GASTOS_TABLE)
        .select("monto, fecha")
        .eq("usuario_id", usuario_id)
        .gte("fecha", str(inicio))
        .lte("fecha", str(fin))
    )
    gastos_data = gastos_query.execute().data or []
    
    # 💾 CÁLCULOS EN MEMORIA (super rápido)
    total_ingresos = float(sum(item.get("monto", 0) for item in ingresos_data))
    total_gastos = float(sum(item.get("monto", 0) for item in gastos_data))
    total_ahorro = max(0, total_ingresos - total_gastos)
    balance = total_ingresos - total_gastos

    return {
        "periodo": {"inicio": str(inicio), "fin": str(fin)},
        "total_ingresos": round(total_ingresos, 2),
        "total_gastos": round(total_gastos, 2),
        "total_ahorro": round(total_ahorro, 2),
        "balance": round(balance, 2),
    }


# 🔧 Funciones auxiliares (mantener por compatibilidad, pero ya no se usan internamente)
def suma_ingresos(usuario_id: str, inicio: date, fin: date) -> float:
    """⚠️ Deprecated: Usa calcular_reporte_rango() para mejor rendimiento"""
    query = (
        supabase.table(INGRESOS_TABLE)
        .select("monto, fecha")
        .eq("usuario_id", usuario_id)
        .gte("fecha", str(inicio))
        .lte("fecha", str(fin))
    )
    data = query.execute().data or []
    return float(sum(item.get("monto", 0) for item in data))


def suma_gastos(usuario_id: str, inicio: date, fin: date) -> float:
    """⚠️ Deprecated: Usa calcular_reporte_rango() para mejor rendimiento"""
    query = (
        supabase.table(GASTOS_TABLE)
        .select("monto, fecha")
        .eq("usuario_id", usuario_id)
        .gte("fecha", str(inicio))
        .lte("fecha", str(fin))
    )
    data = query.execute().data or []
    return float(sum(item.get("monto", 0) for item in data))
