import json
import logging
import os
from datetime import date, datetime, timedelta

import requests

from .llm import parse_gasto
from .sheets import append_gasto
from .analytics.loader import load_dataframe
from .analytics.metrics import kpis, period_bounds
from .analytics.charts import trend_chart, category_bar, maybe_upload_to_s3
from .analytics.suggestions import suggestions

# === Configuración de logging ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "NOT_SET")

# Note: User detection is now handled by AI
# - AI returns "Ignacio" or "Victoria" based on message content
# - If Victoria (or Vicky, Vicki, Viki) is mentioned → "Victoria"
# - Otherwise → "Ignacio" (default)


def handle_stats(args: str) -> str:
    """
    Handle /stats command for expense statistics.
    
    Args:
        args: Command arguments (e.g., "30 USD", "90", "")
        
    Returns:
        Formatted stats message with KPIs and suggestions
    """
    # Parse arguments
    days = 30
    moneda = None
    parts = args.split()
    
    for p in parts:
        if p.isdigit():
            days = int(p)
        elif p.upper() in ("USD", "UYU"):
            moneda = p.upper()
    
    try:
        df = load_dataframe()
        
        if df.empty:
            return "📊 Sin datos disponibles. Registra algunos gastos primero!"
        
        end = date.today()
        start, end = period_bounds(end, days)
        
        data = kpis(df, start, end, moneda)
        s = suggestions(df, end, window_days=days)
        
        # Build response
        lines = [
            f"📊 **Estadísticas** {start} → {end}",
            f"{'(' + moneda + ' únicamente)' if moneda else '(Todas las monedas)'}",
            "",
            f"💰 **Total gastado:** {data['total']:.2f}",
            f"🎫 **Tickets:** {data['tickets']} | **Promedio:** {data['avg_ticket']:.2f}",
            "",
            "🏆 **Top 5 Categorías:**"
        ]
        
        for i, (c, v) in enumerate(list(data['top_categorias'].items())[:5], 1):
            lines.append(f"  {i}. {c.title()}: {v:.2f}")
        
        # Add spending by user if there are multiple
        if len(data['top_quien']) > 1:
            lines.append("")
            lines.append("👥 **Por usuario:**")
            for u, v in data['top_quien'].items():
                lines.append(f"  • {u}: {v:.2f}")
        
        # Add suggestions if any
        if s["savings"]:
            lines.append("")
            lines.append("💡 **Sugerencias de Ahorro:**")
            for i, it in enumerate(s["savings"][:3], 1):
                lines.append(f"  {i}. **{it['categoria'].title()}**: {it['motivo']}")
                lines.append(f"     💡 {it['ahorro']}")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.exception("Error in handle_stats")
        return f"❌ Error generando estadísticas: {str(e)}"


def handle_dashboard(args: str) -> str:
    """
    Handle /dashboard command to generate charts.
    
    Args:
        args: Command arguments (unused for now)
        
    Returns:
        Message with chart URLs or paths
    """
    try:
        df = load_dataframe()
        
        if df.empty:
            return "📊 Sin datos disponibles. Registra algunos gastos primero!"
        
        end = date.today()
        start_90, end_90 = period_bounds(end, 90)
        
        # Generate charts
        path1 = trend_chart(df, filename=f"trend_{end.isoformat()}.png")
        path2 = category_bar(df, start_90, end_90, filename=f"categories_{end.isoformat()}.png")
        
        # Try to upload to S3 (returns local path if not configured)
        url1 = maybe_upload_to_s3(path1)
        url2 = maybe_upload_to_s3(path2)
        
        lines = [
            "📈 **Dashboard Generado**",
            "",
            f"📊 **Tendencia 30d:** {url1}",
            f"📊 **Top Categorías 90d:** {url2}",
            "",
            "💡 Tip: Configura DASHBOARD_S3_BUCKET para recibir links públicos"
        ]
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.exception("Error in handle_dashboard")
        return f"❌ Error generando dashboard: {str(e)}"


def handle_resumen(args: str) -> str:
    """
    Handle /resumen command for period summaries.
    
    Args:
        args: Period specification (e.g., "2025-10", "2025-09-01..2025-09-30")
        
    Returns:
        Formatted summary for the specified period
    """
    try:
        df = load_dataframe()
        
        if df.empty:
            return "📊 Sin datos disponibles. Registra algunos gastos primero!"
        
        # Parse period
        if ".." in args:
            # Range: YYYY-MM-DD..YYYY-MM-DD
            start_str, end_str = args.split("..")
            start = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            end = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()
        elif args.strip():
            # Month: YYYY-MM
            year_month = args.strip()
            dt = datetime.strptime(year_month, "%Y-%m")
            start = dt.date()
            # Last day of month
            next_month = dt.replace(day=28) + timedelta(days=4)
            end = (next_month - timedelta(days=next_month.day)).date()
        else:
            # Default: current month
            today = date.today()
            start = today.replace(day=1)
            end = today
        
        data = kpis(df, start, end, moneda=None)
        
        lines = [
            f"📅 **Resumen** {start} → {end}",
            "",
            f"💰 **Total:** {data['total']:.2f}",
            f"🎫 **Gastos:** {data['tickets']} | **Promedio:** {data['avg_ticket']:.2f}",
            "",
            "📊 **Por Categoría:**"
        ]
        
        for c, v in list(data['top_categorias'].items())[:8]:
            lines.append(f"  • {c.title()}: {v:.2f}")
        
        if len(data['top_quien']) > 1:
            lines.append("")
            lines.append("👥 **Por Usuario:**")
            for u, v in data['top_quien'].items():
                pct = (v / data['total'] * 100) if data['total'] > 0 else 0
                lines.append(f"  • {u}: {v:.2f} ({pct:.0f}%)")
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.exception("Error in handle_resumen")
        return f"❌ Error generando resumen: {str(e)}"

def lambda_handler(event, context):
    """
    Handler principal invocado por AWS Lambda.
    """
    logger.info("=== Lambda handler iniciado ===")
    logger.info(f"Entorno cargado: TELEGRAM_TOKEN={'SET' if TELEGRAM_TOKEN != 'NOT_SET' else 'NOT_SET'}")
    logger.info(f"Evento recibido: {json.dumps(event)[:500]}")  # Limita a 500 chars

    try:
        # 1️⃣ Parsear el body que viene de Telegram
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", {}).get("text", "")
        chat_id = body.get("message", {}).get("chat", {}).get("id")

        logger.info(f"Mensaje recibido: {message}")
        logger.info(f"Chat ID: {chat_id}")
        logger.info(f"Tipo de Chat ID: {type(chat_id)}")

        if not message or not chat_id:
            logger.warning("No se encontró mensaje o chat_id en el evento")
            return {"statusCode": 200, "body": "No message to process"}

        # 1.5️⃣ Handle commands (before expense parsing)
        if message.startswith("/stats"):
            logger.info("Handling /stats command")
            reply = handle_stats(message.replace("/stats", "", 1).strip())
            telegram_response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
            )
            logger.info(f"✅ Stats sent to Telegram (status: {telegram_response.status_code})")
            return {"statusCode": 200, "body": "ok"}
        
        elif message.startswith("/dashboard"):
            logger.info("Handling /dashboard command")
            reply = handle_dashboard(message.replace("/dashboard", "", 1).strip())
            telegram_response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
            )
            logger.info(f"✅ Dashboard sent to Telegram (status: {telegram_response.status_code})")
            return {"statusCode": 200, "body": "ok"}
        
        elif message.startswith("/resumen"):
            logger.info("Handling /resumen command")
            reply = handle_resumen(message.replace("/resumen", "", 1).strip())
            telegram_response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
            )
            logger.info(f"✅ Resumen sent to Telegram (status: {telegram_response.status_code})")
            return {"statusCode": 200, "body": "ok"}
        
        elif message.startswith("/help"):
            logger.info("Handling /help command")
            reply = """
🤖 **Asistente de Gastos - Comandos Disponibles**

📝 **Registrar Gasto:**
Escribe en lenguaje natural, ejemplos:
• "Gasté 1500 en taxi"
• "Victoria: 50 dólares en Amazon"
• "Corte de pelo 1200, Vicky"

📊 **Comandos de Análisis:**
• `/stats` - Estadísticas últimos 30 días
• `/stats 90` - Estadísticas últimos 90 días
• `/stats 30 USD` - Solo gastos en USD
• `/dashboard` - Gráficos de tendencias
• `/resumen 2025-10` - Resumen de octubre 2025
• `/resumen 2025-09-01..2025-09-30` - Rango exacto
• `/help` - Esta ayuda

💱 **Monedas:**
• USD (dólares, u$s, usd)
• UYU (pesos uruguayos, $uy) - default

👥 **Usuarios:**
• Ignacio (default)
• Victoria (menciona: Victoria, Vicky, Vicki, Viki)
"""
            telegram_response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"},
            )
            logger.info(f"✅ Help sent to Telegram (status: {telegram_response.status_code})")
            return {"statusCode": 200, "body": "ok"}

        # 2️⃣ Parsear con Gemini (normal expense message)
        logger.info("Invocando parse_gasto()...")
        gasto = parse_gasto(message)
        logger.info(f"Resultado parseo: {gasto}")

        # 3️⃣ Agregar fecha si no existe
        if not gasto.get("fecha"):
            gasto["fecha"] = date.today().isoformat()
            logger.info(f"Fecha agregada automáticamente: {gasto['fecha']}")

        # 3.5️⃣ Usuario que gastó (siempre Ignacio o Victoria)
        # AI ya determinó quién gastó basado en el mensaje
        # - Si menciona Victoria/Vicky/Vicki/Viki → "Victoria"
        # - Si NO menciona a Victoria → "Ignacio" (default)
        quien = gasto.get("quien", "Ignacio")  # Fallback por seguridad
        gasto["quien"] = quien
        logger.info(f"Usuario registrado: {quien}")

        # 4️⃣ Guardar en Google Sheets
        logger.info("Invocando append_gasto()...")
        append_gasto(gasto)
        logger.info("✅ Gasto registrado en Google Sheets")

        # 5️⃣ Responder en Telegram
        moneda = gasto.get('moneda', 'UYU')
        
        # Currency symbol mapping
        if moneda == 'USD':
            moneda_symbol = 'U$S'
        elif moneda == 'UYU':
            moneda_symbol = '$'
        else:
            moneda_symbol = moneda  # Fallback
        
        reply = (
            f"Registrado ✅\n"
            f"{moneda_symbol} {gasto['monto']} ({moneda})\n"
            f"Categoría: {gasto['categoria']}\n"
            f"Descripción: {gasto['descripcion']}\n"
            f"Fecha: {gasto['fecha']}\n"
            f"Quién: {gasto['quien']}"
        )
        logger.info("Enviando respuesta a Telegram...")
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
        )
        logger.info(f"✅ Mensaje enviado a Telegram (status: {telegram_response.status_code})")

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        logger.exception("❌ Error en lambda_handler")
        return {"statusCode": 200, "body": "error"}
