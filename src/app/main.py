import json
import logging
import os
from datetime import date

import requests

from .llm import parse_gasto
from .sheets import append_gasto

# === Configuración de logging ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "NOT_SET")

# User mapping: chat_id → default user name
USER_MAPPING = {
    807197442: "Ignacio",  # @bigotesecco
    641045556: "User1",    # Update with actual name if known
}

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

        # 2️⃣ Parsear con Gemini
        logger.info("Invocando parse_gasto()...")
        gasto = parse_gasto(message)
        logger.info(f"Resultado parseo: {gasto}")

        # 3️⃣ Agregar fecha si no existe
        if not gasto.get("fecha"):
            gasto["fecha"] = date.today().isoformat()
            logger.info(f"Fecha agregada automáticamente: {gasto['fecha']}")

        # 3.5️⃣ Determinar quién gastó
        # Get default user based on who sent the message
        default_user = USER_MAPPING.get(chat_id, f"User_{chat_id}")
        
        # Check if AI detected a specific user mentioned in the message
        quien_detectado = gasto.get("quien")
        if quien_detectado:
            # User was explicitly mentioned in message (e.g., "Victoria gastó X")
            gasto["quien"] = quien_detectado
            logger.info(f"Usuario detectado en mensaje: {quien_detectado}")
        else:
            # No user mentioned, use the sender's name
            gasto["quien"] = default_user
            logger.info(f"Usuario por defecto (remitente): {default_user}")

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
