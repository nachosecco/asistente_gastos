"""
Analytics module for Asistente de Gastos.

Provides expense analysis, metrics, charts, and actionable suggestions.
"""

from .loader import load_dataframe
from .metrics import kpis, growth_by_category, rolling_trend, anomalies_simple, period_bounds
from .charts import trend_chart, category_bar, maybe_upload_to_s3
from .suggestions import suggestions

__all__ = [
    "load_dataframe",
    "kpis",
    "growth_by_category",
    "rolling_trend",
    "anomalies_simple",
    "period_bounds",
    "trend_chart",
    "category_bar",
    "maybe_upload_to_s3",
    "suggestions",
]

