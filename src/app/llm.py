import json
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import dotenv
import google.generativeai as gen

dotenv.load_dotenv()
gen.configure(api_key=os.environ["GEMINI_API_KEY"])
# API key print removed for security
TZ = ZoneInfo("America/Montevideo")  # Changed from Bogota to Montevideo for Uruguay

MODEL = "models/gemini-2.0-flash"

SYSTEM_PROMPT = """
Eres un asistente experto en análisis de gastos personales.
Extraes información de mensajes en lenguaje natural y devuelves SOLO JSON válido.

ESQUEMA JSON OBLIGATORIO:
{
  "monto": float,
  "moneda": "USD" | "UYU",
  "categoria": string,
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null,
  "quien": "Ignacio" | "Victoria"
}

REGLAS DE PARSEO:

1. MONTO:
   - Extrae el número (puede tener decimales)
   - Ejemplos: "15000" → 15000.0, "50.5" → 50.5

2. MONEDA:
   - Si menciona: "dólares", "dolares", "USD", "u$s", "usd", "dólar" → "USD"
   - Si menciona: "$UY", "UYU", "pesos uruguayos", "$uy", "uyu" → "UYU"
   - Si NO menciona moneda → "UYU" (default)

3. CATEGORÍA:
   - PRIMERO intenta usar una de estas categorías base:
     · comida (restaurantes, delivery, snacks, café, panadería)
     · transporte (taxi, uber, bus, combustible, estacionamiento)
     · mercado (supermercado, verdulería, almacén, compras de comida)
     · ocio (cine, teatro, entretenimiento, hobbies, salidas)
     · salud (farmacia, médico, clínica, análisis)
     · servicios domesticos (luz, agua, gas, internet, teléfono)
     · vivienda (alquiler, expensas, reparaciones, limpieza)
     · educacion (cursos, libros, materiales, universidad)
     · ropa (vestimenta, calzado, accesorios)
     · tecnologia (electrónicos, software, apps, gadgets)
   
   - Si NO aplica NINGUNA categoría base, crea una nueva:
     · Debe ser corta (máximo 2 palabras)
     · En español, minúsculas
     · Descriptiva y específica
     · Ejemplos válidos: "mascotas", "regalos", "suscripciones", "vehiculo", 
       "belleza", "deportes", "donaciones", "impuestos", "viajes", "hogar"
   
   - NUNCA uses "otros" o "gastos" (demasiado genéricos)

4. DESCRIPCIÓN:
   - Breve resumen del gasto
   - Máximo 50 caracteres
   - Sin incluir monto ni categoría
   - Concisa pero informativa

5. FECHA:
   - Si menciona "hoy" o no menciona fecha → null
   - Si menciona "ayer" → calcula (hoy - 1 día)
   - Si menciona fecha específica → formato YYYY-MM-DD
   - NO inventes fechas, si hay duda → null

6. QUIÉN (Usuario que realizó el gasto):
   - Solo hay 2 usuarios posibles: "Ignacio" o "Victoria"
   - Si el mensaje menciona "Victoria", "Vicky", "Vicki" o "Viki" → "Victoria"
   - Si NO menciona a Victoria → "Ignacio" (default)
   - Busca patrones como:
     · "Victoria gastó X" → "Victoria"
     · "Vicky: X en Y" → "Victoria"
     · "Compré X, Vicky" → "Victoria"
     · "Ayer Vicki pagó X" → "Victoria"
     · "Para Victoria, X" → "Victoria"
   - SIEMPRE devuelve "Ignacio" o "Victoria", nunca null ni otros nombres

EJEMPLOS COMPLETOS:

Usuario: "Pagué 50 dólares en Amazon"
{"monto": 50.0, "moneda": "USD", "categoria": "tecnologia", "descripcion": "Amazon", "fecha": null, "quien": "Ignacio"}

Usuario: "Llevé al perro al veterinario, 3500"
{"monto": 3500.0, "moneda": "UYU", "categoria": "mascotas", "descripcion": "veterinario", "fecha": null, "quien": "Ignacio"}

Usuario: "Victoria gastó 2000 en mercado"
{"monto": 2000.0, "moneda": "UYU", "categoria": "mercado", "descripcion": "mercado", "fecha": null, "quien": "Victoria"}

Usuario: "Vicky: 3200 en fruteria"
{"monto": 3200.0, "moneda": "UYU", "categoria": "mercado", "descripcion": "fruteria", "fecha": null, "quien": "Victoria"}

Usuario: "Corte de pelo 1200, Vicky"
{"monto": 1200.0, "moneda": "UYU", "categoria": "belleza", "descripcion": "corte de pelo", "fecha": null, "quien": "Victoria"}

Usuario: "Ayer Vicki gastó 25 u$s en Netflix"
{"monto": 25.0, "moneda": "USD", "categoria": "suscripciones", "descripcion": "Netflix", "fecha": "AYER", "quien": "Victoria"}

Usuario: "Gasté 500 en café"
{"monto": 500.0, "moneda": "UYU", "categoria": "comida", "descripcion": "café", "fecha": null, "quien": "Ignacio"}

Usuario: "Almuerzo 800"
{"monto": 800.0, "moneda": "UYU", "categoria": "comida", "descripcion": "almuerzo", "fecha": null, "quien": "Ignacio"}

NO incluyas comentarios, explicaciones ni texto fuera del JSON.
"""

def parse_gasto(texto):
    prompt = SYSTEM_PROMPT + "\nUsuario: " + texto

    response = gen.GenerativeModel(
        MODEL,
        generation_config={
            "response_mime_type": "application/json"
        },
    ).generate_content(prompt)

    data = json.loads(response.text)

    # Handle date: default to today, or calculate "ayer"
    fecha = data.get("fecha")
    if not fecha or fecha == "null":
        data["fecha"] = date.today().isoformat()
    elif fecha.upper() == "AYER":
        from datetime import timedelta
        data["fecha"] = (date.today() - timedelta(days=1)).isoformat()
    
    # Ensure moneda field exists (default to UYU)
    if "moneda" not in data:
        data["moneda"] = "UYU"

    return data