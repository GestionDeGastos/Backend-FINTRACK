from datetime import date
from src.database.supabase_client import supabase

INGRESOS_TABLE = "ingresos"
GASTOS_TABLE = "gastos"

def suma_ingresos(usuario_id: str, inicio: date, fin: date) -> float:
    """Suma todos los ingresos del usuario en el rango de fechas."""
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
    """Suma todos los gastos del usuario en el rango de fechas."""
    query = (
        supabase.table(GASTOS_TABLE)
        .select("monto, fecha")
        .eq("usuario_id", usuario_id)
        .gte("fecha", str(inicio))
        .lte("fecha", str(fin))
    )
    data = query.execute().data or []
    return float(sum(item.get("monto", 0) for item in data))

def calcular_reporte_rango(usuario_id: str, inicio: date, fin: date) -> dict:
    """
    Calcula los totales de ingresos, gastos, ahorro y balance
    en el rango de fechas dado.
    """
    total_ingresos = suma_ingresos(usuario_id, inicio, fin)
    total_gastos = suma_gastos(usuario_id, inicio, fin)
    total_ahorro = max(0, total_ingresos - total_gastos)
    balance = total_ingresos - total_gastos

    return {
        "periodo": {"inicio": str(inicio), "fin": str(fin)},
        "total_ingresos": round(total_ingresos, 2),
        "total_gastos": round(total_gastos, 2),
        "total_ahorro": round(total_ahorro, 2),
        "balance": round(balance, 2),
    }
