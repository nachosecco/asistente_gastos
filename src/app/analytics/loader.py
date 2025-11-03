"""
Data loader for Google Sheets → pandas DataFrame.

Loads expense data from Google Sheets and converts to properly typed DataFrame.
"""

from __future__ import annotations
import pandas as pd
from dateutil import tz
from datetime import datetime
from ..sheets import read_range

COLUMNS = ["Fecha", "Monto", "Moneda", "Categoría", "Descripción", "Quién"]


def load_dataframe() -> pd.DataFrame:
    """
    Load expenses from Google Sheets into pandas DataFrame.
    
    Returns:
        DataFrame with columns: Fecha, Monto, Moneda, Categoría, Descripción, Quién
        - Fecha: date (America/Montevideo timezone)
        - Monto: float
        - Moneda: str (USD or UYU)
        - Categoría: str (lowercase, normalized)
        - Descripción: str
        - Quién: str (title case)
    
    Notes:
        - Auto-detects and skips header row if present
        - Drops rows with invalid dates or amounts
        - Converts dates to local timezone (Montevideo)
    """
    rows = read_range("registros!A:F")
    
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    
    # Detect if first row is header
    header = rows[0]
    if set(header) >= set(COLUMNS):
        rows = rows[1:]
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=COLUMNS)
    
    # Type conversions
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
    
    # Drop invalid rows
    df = df.dropna(subset=["Fecha", "Monto"]).copy()
    
    # Normalize text fields
    df["Categoría"] = df["Categoría"].str.strip().str.lower()
    df["Moneda"] = df["Moneda"].str.upper().str.strip()
    df["Quién"] = df["Quién"].str.title().str.strip()
    
    # Convert to local timezone (Montevideo) and extract date
    mvd = tz.gettz("America/Montevideo")
    df["Fecha"] = df["Fecha"].dt.tz_localize("UTC").dt.tz_convert(mvd).dt.date
    
    return df

