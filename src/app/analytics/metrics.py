"""
Metrics calculation for expense analytics.

Provides KPIs, growth analysis, trends, and anomaly detection.
"""

from __future__ import annotations
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional

Period = Tuple[date, date]  # (start_date, end_date) inclusive


def date_range(df: pd.DataFrame) -> Optional[Period]:
    """
    Get the date range of the DataFrame.
    
    Args:
        df: DataFrame with Fecha column
        
    Returns:
        Tuple of (min_date, max_date) or None if empty
    """
    if df.empty:
        return None
    return (df["Fecha"].min(), df["Fecha"].max())


def filter_period(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """
    Filter DataFrame to a specific date range (inclusive).
    
    Args:
        df: DataFrame with Fecha column
        start: Start date (inclusive)
        end: End date (inclusive)
        
    Returns:
        Filtered DataFrame copy
    """
    return df[(df["Fecha"] >= start) & (df["Fecha"] <= end)].copy()


def period_bounds(end: date, days: int) -> Period:
    """
    Calculate period bounds given an end date and number of days.
    
    Args:
        end: End date
        days: Number of days to go back
        
    Returns:
        Tuple of (start_date, end_date)
        
    Example:
        period_bounds(date(2025, 11, 3), 30)
        → (date(2025, 10, 5), date(2025, 11, 3))
    """
    start = end - timedelta(days=days - 1)
    return (start, end)


def kpis(
    df: pd.DataFrame,
    start: date,
    end: date,
    moneda: Optional[str] = None
) -> Dict:
    """
    Calculate key performance indicators for a period.
    
    Args:
        df: DataFrame with expense data
        start: Period start date
        end: Period end date
        moneda: Optional currency filter ("USD" or "UYU")
        
    Returns:
        Dict with:
            - total: Total spent in period
            - tickets: Number of expenses
            - avg_ticket: Average expense amount
            - top_categorias: Top 10 categories by amount
            - top_quien: Spending by user
    """
    # Filter by period
    d = filter_period(df, start, end)
    
    # Filter by currency if specified
    if moneda:
        d = d[d["Moneda"] == moneda]
    
    total = d["Monto"].sum()
    
    # Aggregations
    por_cat = d.groupby("Categoría")["Monto"].sum().sort_values(ascending=False)
    por_quien = d.groupby("Quién")["Monto"].sum().sort_values(ascending=False)
    
    tickets = len(d)
    avg_ticket = float(total / tickets) if tickets > 0 else 0.0
    
    return {
        "total": float(total),
        "tickets": tickets,
        "avg_ticket": avg_ticket,
        "top_categorias": por_cat.head(10).to_dict(),
        "top_quien": por_quien.to_dict(),
    }


def growth_by_category(
    df: pd.DataFrame,
    curr_start: date,
    curr_end: date,
    prev_start: date,
    prev_end: date
) -> List[Dict]:
    """
    Calculate growth by category comparing two periods.
    
    Args:
        df: DataFrame with expense data
        curr_start: Current period start
        curr_end: Current period end
        prev_start: Previous period start
        prev_end: Previous period end
        
    Returns:
        List of dicts with:
            - categoria: Category name
            - actual: Current period total
            - previo: Previous period total
            - delta: Absolute change
            - pct: Percentage change
        
        Sorted by percentage change (descending)
    """
    cur = filter_period(df, curr_start, curr_end)
    prv = filter_period(df, prev_start, prev_end)
    
    cur_g = cur.groupby("Categoría")["Monto"].sum()
    prv_g = prv.groupby("Categoría")["Monto"].sum()
    
    cats = set(cur_g.index) | set(prv_g.index)
    
    out = []
    for c in cats:
        a = float(cur_g.get(c, 0.0))
        b = float(prv_g.get(c, 0.0))
        delta = a - b
        
        if b > 0:
            pct = (delta / b) * 100.0
        elif a > 0 and b == 0:
            pct = 100.0  # New category with spending
        else:
            pct = 0.0
        
        out.append({
            "categoria": c,
            "actual": a,
            "previo": b,
            "delta": delta,
            "pct": pct
        })
    
    # Sort by percentage change (highest first)
    out.sort(key=lambda x: x["pct"], reverse=True)
    
    return out


def rolling_trend(df: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
    """
    Calculate rolling average trend.
    
    Args:
        df: DataFrame with expense data
        window_days: Rolling window size in days
        
    Returns:
        DataFrame with:
            - total: Daily total spending
            - roll_{window_days}: Rolling average
            
        Index: Date
    """
    # Daily sum
    daily = df.groupby("Fecha")["Monto"].sum().sort_index()
    
    # Rolling mean
    roll = daily.rolling(
        window=window_days,
        min_periods=max(1, window_days // 3)
    ).mean()
    
    return pd.DataFrame({
        "total": daily,
        f"roll_{window_days}": roll
    })


def anomalies_simple(
    df: pd.DataFrame,
    per_cat: bool = True,
    z: float = 2.0
) -> Dict | List[Dict]:
    """
    Detect anomalies using z-score method.
    
    Args:
        df: DataFrame with expense data
        per_cat: If True, detect anomalies per category; if False, overall
        z: Z-score threshold (default 2.0 = ~95% confidence)
        
    Returns:
        If per_cat=True: Dict mapping category → list of anomalies
        If per_cat=False: List of anomalies
        
        Each anomaly is a dict with:
            - fecha: Date string
            - monto: Amount
            - z: Z-score
    """
    def _detect_anomalies(df0: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in a single DataFrame."""
        daily = df0.groupby("Fecha")["Monto"].sum()
        
        if len(daily) < 5:
            return []
        
        mu = daily.mean()
        sd = daily.std(ddof=0)
        
        if sd == 0:
            return []
        
        anomalies = []
        for idx, val in daily.items():
            z_score = (val - mu) / sd
            if abs(z_score) >= z:
                anomalies.append({
                    "fecha": str(idx),
                    "monto": float(val),
                    "z": float(z_score)
                })
        
        return anomalies
    
    if not per_cat:
        return _detect_anomalies(df)
    
    # Per category
    out = {}
    for cat, dfx in df.groupby("Categoría"):
        res = _detect_anomalies(dfx)
        if res:
            out[cat] = res
    
    return out

