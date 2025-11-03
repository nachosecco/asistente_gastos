"""
Chart generation using matplotlib.

Creates PNG charts for trends and category analysis.
Optional S3 upload for sharing via Telegram.
"""

from __future__ import annotations
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Lambda
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date
from typing import Optional
from .metrics import rolling_trend, filter_period

# Lambda writes to /tmp
TMP_DIR = "/tmp"

# Try to import boto3 (optional for S3 uploads)
try:
    import boto3
    _HAS_BOTO = True
except ImportError:
    _HAS_BOTO = False


def _save_fig(fig, filename: str) -> str:
    """
    Save matplotlib figure to /tmp directory.
    
    Args:
        fig: Matplotlib figure object
        filename: Output filename (e.g., "trend.png")
        
    Returns:
        Full path to saved file
    """
    path = os.path.join(TMP_DIR, filename)
    fig.savefig(path, bbox_inches='tight', dpi=100)
    plt.close(fig)
    return path


def trend_chart(df: pd.DataFrame, filename: str = "trend.png") -> str:
    """
    Generate trend chart with daily totals and 30-day rolling average.
    
    Args:
        df: DataFrame with expense data
        filename: Output filename
        
    Returns:
        Path to saved PNG file
    """
    tr = rolling_trend(df, window_days=30)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    tr["total"].plot(ax=ax, label="Gasto diario", alpha=0.6, linewidth=1)
    tr["roll_30"].plot(ax=ax, label="Media móvil 30d", linewidth=2)
    
    ax.set_title("Tendencia de Gastos - Diario y Media Móvil 30d", fontsize=14, fontweight='bold')
    ax.set_xlabel("Fecha", fontsize=11)
    ax.set_ylabel("Monto", fontsize=11)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return _save_fig(fig, filename)


def category_bar(
    df: pd.DataFrame,
    start: date,
    end: date,
    filename: str = "categorias.png",
    top_n: int = 12
) -> str:
    """
    Generate bar chart of top categories for a period.
    
    Args:
        df: DataFrame with expense data
        start: Period start date
        end: Period end date
        filename: Output filename
        top_n: Number of top categories to show
        
    Returns:
        Path to saved PNG file
    """
    d = filter_period(df, start, end)
    
    if d.empty:
        # Create empty chart
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, 'Sin datos para este período',
                ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return _save_fig(fig, filename)
    
    top = d.groupby("Categoría")["Monto"].sum().sort_values(ascending=False).head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top.plot(kind="bar", ax=ax, color='steelblue', edgecolor='black', linewidth=0.5)
    
    ax.set_title(f"Top {top_n} Categorías: {start} → {end}", fontsize=14, fontweight='bold')
    ax.set_xlabel("Categoría", fontsize=11)
    ax.set_ylabel("Monto Total", fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(top):
        ax.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    return _save_fig(fig, filename)


def maybe_upload_to_s3(local_path: str) -> str:
    """
    Upload chart to S3 if bucket is configured.
    
    Args:
        local_path: Path to local PNG file
        
    Returns:
        S3 URL if uploaded, otherwise local path
        
    Environment Variables:
        - DASHBOARD_S3_BUCKET: S3 bucket name (optional)
        - AWS_REGION: AWS region (default: us-east-1)
    """
    bucket = os.getenv("DASHBOARD_S3_BUCKET")
    
    # Return local path if no bucket configured or boto3 not available
    if not bucket or not _HAS_BOTO:
        return local_path
    
    # Upload to S3
    key = os.path.basename(local_path)
    s3 = boto3.client("s3")
    
    try:
        s3.upload_file(
            local_path,
            bucket,
            key,
            ExtraArgs={
                "ContentType": "image/png",
                "ACL": "public-read"
            }
        )
        
        region = os.getenv("AWS_REGION", "us-east-1")
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        
        return url
        
    except Exception as e:
        # Log error but return local path as fallback
        import logging
        logger = logging.getLogger()
        logger.error(f"Failed to upload to S3: {e}")
        return local_path

