from typing import Dict

def analizar_plan(plan_data: Dict) -> Dict:
    """
    Analiza los datos de un plan financiero guardado y genera estadísticas
    y recomendaciones personalizadas.
    """

    ingreso_total = plan_data.get("ingreso_total", 0)
    ahorro_deseado = plan_data.get("ahorro_deseado", 0)
    distribucion = plan_data.get("distribucion_gastos", {}) or {}

    if not ingreso_total or not distribucion:
        return {"error": "Datos del plan incompletos para el análisis."}

    # Calcular totales
    total_gastos = sum(distribucion.values())
    porcentaje_ahorro = round((ahorro_deseado / ingreso_total) * 100, 2) if ingreso_total else 0

    # Categorías más y menos costosas
    categoria_mayor = max(distribucion, key=distribucion.get)
    categoria_menor = min(distribucion, key=distribucion.get)

    # Recomendaciones básicas
    recomendaciones = []

    if porcentaje_ahorro < 10:
        recomendaciones.append("Intenta aumentar tu ahorro al menos al 10% de tus ingresos.")
    if distribucion.get("entretenimiento", 0) > ingreso_total * 0.15:
        recomendaciones.append("Reduce tus gastos en entretenimiento para mejorar tu balance.")
    if distribucion.get("alimentación", 0) < ingreso_total * 0.2:
        recomendaciones.append("Podrías destinar un poco más a alimentación si lo necesitas.")
    if distribucion.get("vivienda", 0) > ingreso_total * 0.35:
        recomendaciones.append("Considera reducir gastos en vivienda si es posible.")

    return {
        "total_gastos": total_gastos,
        "porcentaje_ahorro": porcentaje_ahorro,
        "categoria_mayor_gasto": categoria_mayor,
        "categoria_menor_gasto": categoria_menor,
        "recomendaciones": recomendaciones
    }
