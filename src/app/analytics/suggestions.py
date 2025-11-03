"""
Actionable suggestions based on spending patterns.

Provides savings tips, spending reordering advice, and overspending detection.
"""

from __future__ import annotations
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List
from .metrics import filter_period, growth_by_category

# Knowledge base: category-specific tips
RULES_DOC = {
    "suscripciones": {
        "tip": "Revisa suscripciones mensuales. Cancela o baja de plan si no usas ≥80% del valor percibido.",
        "reorder": "Alinea los cobros al inicio de mes para controlar presupuesto."
    },
    "mercado": {
        "tip": "Compra por mayor/clubes de precio y arma lista semanal para reducir compras impulsivas.",
        "reorder": "Concentra compras en 1–2 visitas/mes para reducir impulsos."
    },
    "transporte": {
        "tip": "Planifica viajes, comparte traslados o considera abonos mensuales.",
        "reorder": "Agrupa diligencias para reducir viajes cortos innecesarios."
    },
    "comida": {
        "tip": "Prepara comidas en casa, reduce delivery. Batch cooking ahorra tiempo y dinero.",
        "reorder": "Planifica menú semanal para evitar compras de emergencia."
    },
    "salud": {
        "tip": "Revisa cobertura de seguro médico. Considera plan con copagos bajos si usas mucho.",
        "reorder": "Agenda consultas preventivas para evitar emergencias costosas."
    },
    "tecnologia": {
        "tip": "Compara precios online. Aprovecha ofertas anuales (ej. Black Friday).",
        "reorder": "Espera al menos 30 días antes de compras >$100 (reduce impulsos)."
    },
    "ropa": {
        "tip": "Compra fuera de temporada. Revisa armario antes de comprar para evitar duplicados.",
        "reorder": "Establece presupuesto trimestral y compra en lotes."
    },
    "ocio": {
        "tip": "Busca alternativas gratuitas/económicas (parques, museos días gratis).",
        "reorder": "Planifica entretenimiento mensual, evita gastos impulsivos."
    },
    "servicios domesticos": {
        "tip": "Compara proveedores anualmente. Reduce consumo (luces LED, bajo flujo agua).",
        "reorder": "Revisa contratos al vencimiento, negocia descuentos por fidelidad."
    },
    "belleza": {
        "tip": "Considera productos multi-uso. Extiende intervalos entre servicios si es posible.",
        "reorder": "Agenda servicios con anticipación para aprovechar promociones."
    },
}

# Default rule for categories not in the knowledge base
DEFAULT_RULE = {
    "tip": "Establece un presupuesto mensual para esta categoría y revisa gastos semanalmente.",
    "reorder": "Agrupa y agenda este tipo de gasto para mejor control."
}


def suggestions(
    df: pd.DataFrame,
    end: date,
    window_days: int = 30,
    overspend_threshold_pct: float = 25.0,
    overspend_threshold_abs: float = 1000.0
) -> Dict:
    """
    Generate actionable suggestions based on spending patterns.
    
    Compares current period vs previous period to detect:
    - Overspending (categories with ≥25% increase and ≥1000 absolute)
    - Provides savings tips and reordering advice
    
    Args:
        df: DataFrame with expense data
        end: End date for analysis
        window_days: Period length in days
        overspend_threshold_pct: Percentage increase threshold (default 25%)
        overspend_threshold_abs: Absolute amount threshold (default 1000)
        
    Returns:
        Dict with:
            - overspend: List of categories exceeding both thresholds
            - savings: List of actionable savings tips
            - inadecuado: Top 3 overspending categories
    """
    # Define periods
    cur_start = end - timedelta(days=window_days - 1)
    prv_start = cur_start - timedelta(days=window_days)
    prv_end = cur_start - timedelta(days=1)
    
    # Calculate growth by category
    growth = growth_by_category(df, cur_start, end, prv_start, prv_end)
    
    # Identify overspending: ≥25% increase AND ≥1000 in current period
    overspend = [
        g for g in growth
        if g["pct"] >= overspend_threshold_pct and g["actual"] >= overspend_threshold_abs
    ]
    
    # Generate savings suggestions
    savings = []
    for g in overspend:
        c = g["categoria"]
        rule = RULES_DOC.get(c, DEFAULT_RULE)
        
        savings.append({
            "categoria": c,
            "motivo": f"↑ {g['pct']:.0f}% vs período previo ({g['delta']:.0f} más)",
            "actual": g['actual'],
            "previo": g['previo'],
            "ahorro": rule["tip"],
            "reorden": rule["reorder"],
        })
    
    # Top 3 most problematic (by percentage AND absolute change)
    inadecuado = sorted(
        overspend,
        key=lambda x: (x["pct"], x["delta"]),
        reverse=True
    )[:3]
    
    return {
        "overspend": overspend[:10],
        "savings": savings[:10],
        "inadecuado": inadecuado
    }

