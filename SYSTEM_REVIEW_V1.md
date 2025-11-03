# 🔍 Complete System Review - Version 1.0

**Review Date:** November 3, 2025  
**Current Version:** 1.0 (Production)  
**Next Version:** 2.0 (Improvements)

---

## 📊 Complete Data Flow

### End-to-End Mechanism

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: USER SENDS MESSAGE                                  │
│                                                              │
│ Telegram App → @gastos_secco_grignola_bot                   │
│ Message: "Gasté 15000 en taxi"                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: TELEGRAM WEBHOOK TO LAMBDA                          │
│                                                              │
│ Telegram API sends HTTP POST to:                            │
│ https://cvgz2ovruhpn3qu2iinvwn2bvi0ylozl.lambda-url...     │
│                                                              │
│ Payload (JSON):                                              │
│ {                                                            │
│   "message": {                                               │
│     "text": "Gasté 15000 en taxi",                          │
│     "chat": {"id": 807197442}                               │
│   }                                                          │
│ }                                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: LAMBDA HANDLER (main.py)                            │
│                                                              │
│ lambda_handler(event, context):                             │
│   1. Parse event body (JSON.parse)                          │
│   2. Extract: message text & chat_id                        │
│   3. Log received message                                   │
│   4. Call parse_gasto(message) → llm.py                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: AI PARSING (llm.py)                                 │
│                                                              │
│ parse_gasto("Gasté 15000 en taxi"):                         │
│   1. Build prompt: SYSTEM_PROMPT + user message             │
│   2. Call Google Gemini 2.0 Flash                           │
│   3. Force JSON response (response_mime_type)               │
│   4. Parse JSON response                                    │
│   5. Add default date if missing                            │
│                                                              │
│ Gemini AI Analyzes:                                         │
│   Input: "Gasté 15000 en taxi"                              │
│   ↓                                                          │
│   Output: {                                                  │
│     "monto": 15000.0,                                        │
│     "categoria": "transporte",                              │
│     "descripcion": "taxi",                                  │
│     "fecha": null → becomes "2025-11-03"                    │
│   }                                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: USER IDENTIFICATION (main.py)                       │
│                                                              │
│ if chat_id == 641045556:                                    │
│     quien = "User1"                                         │
│ else:                                                        │
│     quien = "User2"  ← You are this!                        │
│                                                              │
│ gasto["quien"] = quien                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: SAVE TO GOOGLE SHEETS (sheets.py)                   │
│                                                              │
│ append_gasto(gasto):                                        │
│   1. Get Google Service Account credentials (base64)        │
│   2. Build Google Sheets API client                         │
│   3. Create row: [fecha, monto, categoria, descripcion,     │
│      quien]                                                  │
│   4. Append to range "registros!A:D" ← BUG! Should be A:E   │
│                                                              │
│ Google Sheet Result:                                         │
│   2025-11-03 | 15000 | transporte | taxi | User2            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: SEND TELEGRAM RESPONSE (main.py)                    │
│                                                              │
│ Builds reply message:                                        │
│   "Registrado ✅                                             │
│    15000 COP                                                 │
│    Categoría: transporte                                    │
│    Descripción: taxi                                        │
│    Fecha: 2025-11-03                                        │
│    Quién: User2"                                            │
│                                                              │
│ POST to Telegram API:                                        │
│   https://api.telegram.org/bot<TOKEN>/sendMessage           │
│   {"chat_id": 807197442, "text": reply}                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: USER RECEIVES CONFIRMATION                          │
│                                                              │
│ Telegram → Your phone/desktop                               │
│ Shows confirmation message with all details                  │
└─────────────────────────────────────────────────────────────┘

Total Time: 2-5 seconds
```

---

## 🔧 Current Implementation Details

### 1. **main.py - Lambda Handler**

**Input:** Telegram webhook event (JSON)  
**Output:** `{"statusCode": 200, "body": "ok"}`

**Process:**
```python
1. event.body → JSON.parse → extract message & chat_id
2. message → parse_gasto() → gasto dict
3. Add "quien" based on chat_id (hardcoded mapping)
4. gasto → append_gasto() → writes to Google Sheets
5. Build reply → POST to Telegram API
6. Return 200 (Telegram needs this)
```

**Issues Found:**
- ❌ Line 62: Says "COP" but should be currency-aware
- ❌ Lines 49-52: Hardcoded user mapping (not scalable)
- ❌ Line 11: API key printed to logs (security risk)

---

### 2. **llm.py - AI Parsing**

**Input:** String (expense message in natural language)  
**Output:** Dict with monto, categoria, descripcion, fecha

**Process:**
```python
1. SYSTEM_PROMPT + user message → combined prompt
2. Gemini 2.0 Flash with JSON enforcement
3. Parse JSON response
4. Default fecha = today if null
5. Return structured data
```

**Current Prompt Analysis:**

**Strengths:**
- ✅ Clear JSON schema
- ✅ JSON response enforcement
- ✅ Date handling rules
- ✅ Predefined categories

**Weaknesses:**
- ❌ Fixed category list → forces "otros" for unknowns
- ❌ No currency support (assumes single currency)
- ❌ No validation of parsed data
- ❌ API key printed to logs (line 11)

**Current Categories:**
```
servicios domesticos, gastos, comida, transporte, 
mercado, ocio, salud, otros
```

**Issue:** "otros" becomes a catch-all bucket → not useful for analysis

---

### 3. **sheets.py - Google Sheets Writer**

**Input:** Gasto dict  
**Output:** New row in Google Sheet

**Process:**
```python
1. Decode base64 credentials
2. Build Sheets API client
3. Create row: [fecha, monto, categoria, descripcion, quien]
4. Append to "registros!A:D"
5. Execute API call
```

**Critical Bug:**
```python
range="registros!A:D"  # A:D = 4 columns
values = [[fecha, monto, categoria, descripcion, quien]]  # 5 values!
```

**This works by accident!** Google Sheets auto-expands the range, but it's wrong.

**Should be:** `range="registros!A:E"`

**No Error Handling:**
- ❌ No try/except for Google API failures
- ❌ No validation of credentials
- ❌ No retry logic for transient failures

---

## 📋 Current System Capabilities

### ✅ What Works Well

1. **Natural Language Understanding**
   - "Gasté 15000 en taxi" ✅
   - "Pagué 45000 en el mercado" ✅
   - "Comí pizza por 20000" ✅

2. **Automatic Categorization**
   - Gemini AI picks appropriate category
   - Pretty accurate for common expenses

3. **Serverless Architecture**
   - Scales automatically
   - Pay per use
   - No server management

4. **Real-time Processing**
   - 2-5 second response time
   - Includes cold starts

5. **Data Persistence**
   - Google Sheets (accessible anywhere)
   - No database needed

---

### ❌ Current Limitations

1. **Single Currency**
   - Assumes all amounts are in same currency
   - Shows "COP" hardcoded (Colombian Pesos)
   - Can't track USD/UYU separately

2. **Fixed Categories**
   - Only 8 predefined categories
   - Unknown expenses → "otros"
   - Can't create custom categories

3. **Hardcoded User Mapping**
   - Only 2 users supported
   - Chat IDs hardcoded
   - Not scalable

4. **No Data Validation**
   - Doesn't check for negative amounts
   - Doesn't validate category names
   - No duplicate detection

5. **Limited Error Handling**
   - Google Sheets errors crash silently
   - No retry logic
   - Returns "error" but doesn't specify what failed

6. **Security Issues**
   - API key exposed in logs (line 11 in llm.py)
   - Lambda URL is public (required, but no validation)

---

## 🎯 Version 2.0 Improvements Plan

### Feature 1: Multi-Currency Support

**Goal:** Track USD and UYU separately

**Changes Required:**
1. Update JSON schema to include `moneda` field
2. Update prompt to detect currency from text
3. Add currency column to Google Sheet
4. Update Telegram response to show correct symbol

**AI Detection Examples:**
- "Gasté 50 dólares" → USD
- "Pagué 1500 pesos uruguayos" → UYU  
- "100 u$s" → USD
- "500 $uy" → UYU
- "1000" (no currency) → Default to UYU

### Feature 2: Dynamic Category Creation

**Goal:** Let AI create meaningful categories instead of "otros"

**Changes Required:**
1. Update prompt with examples of good categories
2. Extend base category list
3. Allow AI to create new short categories
4. Remove "otros" from allowed list

**New Category Strategy:**

**Base Categories (always use if applicable):**
```
comida, transporte, mercado, ocio, salud, 
servicios domesticos, vivienda, educacion, ropa, tecnologia
```

**Dynamic Categories (AI creates if needed):**
```
Examples: 
- mascotas (veterinarian, pet food)
- regalos (birthday gifts, presents)
- suscripciones (Netflix, Spotify, etc.)
- vehiculo (car maintenance, insurance)
- belleza (haircut, cosmetics)
- deportes (gym, equipment)
```

**Rules for AI:**
- Use base category if expense clearly fits
- Create new category if no base fits (max 2 words, Spanish, lowercase)
- Be specific, not generic
- Don't use "otros" ever

### Feature 3: Fix Known Bugs

1. ❌ Remove API key print (llm.py:11)
2. ❌ Fix Sheets range A:D → A:F (will be 6 columns with currency)
3. ❌ Add error handling to sheets.py
4. ❌ Fix timezone (should be configurable)

---

## 📐 Version 2.0 Data Schema

### Current (v1.0):
```python
{
  "monto": float,
  "categoria": string,  # Fixed list
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null,
  "quien": string  # Added by main.py
}
```

### Proposed (v2.0):
```python
{
  "monto": float,
  "moneda": "USD" | "UYU",  # NEW!
  "categoria": string,  # Dynamic
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null,
  "quien": string  # Added by main.py
}
```

### Google Sheet Structure

**Current:**
```
A: Fecha | B: Monto | C: Categoría | D: Descripción | E: Quién
```

**Proposed:**
```
A: Fecha | B: Monto | C: Moneda | D: Categoría | E: Descripción | F: Quién
```

---

## 🧪 Test Cases for v2.0

### Test 1: USD Detection
```
Input: "Pagué 50 dólares en Amazon"
Expected: {
  monto: 50.0,
  moneda: "USD",
  categoria: "tecnologia",
  descripcion: "Amazon",
  fecha: "2025-11-03"
}
```

### Test 2: UYU Default
```
Input: "Gasté 500 en taxi"
Expected: {
  monto: 500.0,
  moneda: "UYU",  # Default
  categoria: "transporte",
  descripcion: "taxi",
  fecha: "2025-11-03"
}
```

### Test 3: Dynamic Category Creation
```
Input: "Llevé al perro al veterinario, 3500 pesos"
Expected: {
  monto: 3500.0,
  moneda: "UYU",
  categoria: "mascotas",  # AI creates this!
  descripcion: "veterinario perro",
  fecha: "2025-11-03"
}
```

### Test 4: Multiple Currencies
```
Input: "Pagué 100 dólares de Netflix"
Expected: {
  monto: 100.0,
  moneda: "USD",
  categoria: "suscripciones",  # AI creates this!
  descripcion: "Netflix",
  fecha: "2025-11-03"
}
```

### Test 5: Edge Case - No Category Fits
```
Input: "Doné 1000 a una ONG"
Expected: {
  monto: 1000.0,
  moneda: "UYU",
  categoria: "donaciones",  # AI creates this!
  descripcion: "ONG",
  fecha: "2025-11-03"
}
```

---

## 🔄 Migration Strategy

### Breaking Changes

**Google Sheet:**
- ✅ Need to add "Moneda" column (column C)
- ✅ Existing data won't have currency → can backfill with "UYU"

**Telegram Response:**
- ✅ Format changes from "15000 COP" to "$ 15000 (UYU)"
- ✅ Non-breaking for users (just different format)

**Categories:**
- ✅ New categories will appear
- ✅ Old data keeps existing categories
- ✅ More granular categorization going forward

### Migration Steps

1. **Update Google Sheet:**
   - Insert new column C: "Moneda"
   - Shift existing columns right

2. **Deploy v2.0 Code:**
   - Update llm.py (new prompt)
   - Update sheets.py (6 columns, range A:F)
   - Update main.py (currency-aware response)

3. **Test:**
   - Send USD expense
   - Send UYU expense
   - Send expense that needs new category
   - Verify all appear correctly

4. **Backfill (optional):**
   - Add "UYU" to all existing rows in column C

---

## 💡 Improved Prompt Design (v2.0)

### Strategy Changes

**Current Prompt:**
- ❌ Fixed category list → limiting
- ❌ "otros" as fallback → not descriptive
- ❌ No currency handling

**v2.0 Prompt:**
- ✅ Base categories + dynamic creation
- ✅ Currency detection (USD/UYU)
- ✅ Smarter categorization
- ✅ Examples for edge cases

### Proposed Prompt Structure

```python
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
   - Si menciona: "dólares", "USD", "u$s", "dolares" → "USD"
   - Si menciona: "$UY", "UYU", "pesos uruguayos" → "UYU"
   - Si NO menciona nada → "UYU" (default)

3. CATEGORÍA:
   - PRIMERO intenta usar una de estas categorías base:
     · comida (restaurantes, delivery, snacks, café)
     · transporte (taxi, uber, bus, gasolina)
     · mercado (supermercado, verdulería, almacén)
     · ocio (cine, teatro, entretenimiento, hobbies)
     · salud (farmacia, médico, clínica)
     · servicios domesticos (luz, agua, gas, internet)
     · vivienda (alquiler, mantenimiento)
     · educacion (cursos, libros, universidad)
     · ropa (vestimenta, calzado)
     · tecnologia (electrónicos, software)
   
   - Si NO aplica NINGUNA categoría base, crea una nueva categoría:
     · Debe ser corta (máximo 2 palabras)
     · En español, minúsculas
     · Descriptiva y específica
     · Ejemplos: "mascotas", "regalos", "suscripciones", "vehiculo", 
                 "belleza", "deportes", "donaciones", "impuestos"
   
   - NUNCA uses "otros" o "gastos" genéricos

4. DESCRIPCIÓN:
   - Breve resumen del gasto
   - Máximo 50 caracteres
   - Sin el monto ni la categoría

5. FECHA:
   - Si menciona fecha explícita → parsea formato YYYY-MM-DD
   - Si dice "ayer" → calcula fecha de ayer
   - Si dice "hoy" o no menciona → null (se agrega automáticamente)
   - NO inventes fechas

EJEMPLOS:

Entrada: "Pagué 50 dólares en Amazon"
Salida: {"monto": 50.0, "moneda": "USD", "categoria": "tecnologia", "descripcion": "Amazon", "fecha": null}

Entrada: "Llevé al perro al veterinario, 3500"
Salida: {"monto": 3500.0, "moneda": "UYU", "categoria": "mascotas", "descripcion": "veterinario", "fecha": null}

Entrada: "Ayer gasté 25 u$s en Netflix"
Salida: {"monto": 25.0, "moneda": "USD", "categoria": "suscripciones", "descripcion": "Netflix", "fecha": "2025-11-02"}

Entrada: "Compré flores para mi mamá, 800 pesos uruguayos"
Salida: {"monto": 800.0, "moneda": "UYU", "categoria": "regalos", "descripcion": "flores para mamá", "fecha": null}

NO incluyas comentarios, explicaciones ni texto adicional. SOLO el JSON.
"""
```

---

## 🎨 Benefits of New Approach

### Dynamic Categories

**Before (v1.0):**
```
"Doné 1000 a Cruz Roja" → categoria: "otros"  ❌ Not descriptive
"Pagué Netflix 500" → categoria: "otros"      ❌ Not descriptive
"Peluquería 1200" → categoria: "otros"        ❌ Not descriptive
```

**After (v2.0):**
```
"Doné 1000 a Cruz Roja" → categoria: "donaciones"      ✅ Clear!
"Pagué Netflix 500" → categoria: "suscripciones"       ✅ Clear!
"Peluquería 1200" → categoria: "belleza"               ✅ Clear!
```

### Multi-Currency

**Before (v1.0):**
```
"Pagué 50 dólares" → 50 COP  ❌ Wrong currency!
```

**After (v2.0):**
```
"Pagué 50 dólares" → U$S 50 (USD)  ✅ Correct!
"Gasté 1500 pesos" → $ 1500 (UYU)  ✅ Correct!
```

---

## 📊 Impact Analysis

### Code Changes Required

| File | Lines Changed | Complexity | Impact |
|------|---------------|------------|---------|
| llm.py | ~30 lines | Medium | Prompt rewrite |
| sheets.py | ~5 lines | Low | Add currency column |
| main.py | ~8 lines | Low | Update response format |
| Google Sheet | 1 column | Low | Manual: insert column |

**Total:** ~45 lines of code changes

### Testing Required

1. Test USD detection (5 test cases)
2. Test UYU detection (5 test cases)
3. Test default currency (3 test cases)
4. Test dynamic categories (10+ test cases)
5. Test base categories still work (8 test cases)
6. Test date parsing still works (5 test cases)

**Total:** ~36 test cases

### Rollback Strategy

If v2.0 has issues:
```bash
# 1. Checkout main branch
git checkout main

# 2. Rebuild and redeploy
docker buildx build --platform linux/amd64 -t asistente-gastos:latest .
docker tag asistente-gastos:latest 344666582324.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest
docker push 344666582324.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest

# 3. Update Lambda
source /tmp/aws-credentials.sh
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri 344666582324.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest \
  --region us-east-1
```

---

## 🚀 Ready for v2.0?

**I'll now:**
1. ✅ Create branch `assistente_v2.0`
2. ✅ Implement multi-currency support
3. ✅ Implement dynamic categories
4. ✅ Fix all known bugs
5. ✅ Add error handling
6. ✅ Update documentation

**Then you can:**
- Test in the branch
- Deploy when ready
- Merge to main when confident

**Let's build v2.0!** 🔥


