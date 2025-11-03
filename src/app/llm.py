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
  "fecha": "YYYY-MM-DD" | null
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

EJEMPLOS COMPLETOS:

Usuario: "Pagué 50 dólares en Amazon"
{"monto": 50.0, "moneda": "USD", "categoria": "tecnologia", "descripcion": "Amazon", "fecha": null}

Usuario: "Llevé al perro al veterinario, 3500"
{"monto": 3500.0, "moneda": "UYU", "categoria": "mascotas", "descripcion": "veterinario", "fecha": null}

Usuario: "Ayer gasté 25 u$s en Netflix"
{"monto": 25.0, "moneda": "USD", "categoria": "suscripciones", "descripcion": "Netflix", "fecha": "AYER"}

Usuario: "Compré flores, 800 pesos uruguayos"
{"monto": 800.0, "moneda": "UYU", "categoria": "regalos", "descripcion": "flores", "fecha": null}

Usuario: "Corte de pelo 1200"
{"monto": 1200.0, "moneda": "UYU", "categoria": "belleza", "descripcion": "corte de pelo", "fecha": null}

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