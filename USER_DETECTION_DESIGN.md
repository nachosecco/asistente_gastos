# 👥 User Detection System - Design Document

**Branch:** `fix-username`  
**Goal:** Smart user identification for shared expense tracking

---

## 🎯 Requirements

### Current Behavior (Hardcoded)
```python
if chat_id == 641045556:
    quien = "User1"
else:
    quien = "User2"
```
❌ Not flexible, not user-friendly

### Desired Behavior

#### Scenario 1: Default User (Sender)
```
Chat ID: 807197442 (@bigotesecco)
Message: "Gasté 1500 en taxi"
Result: quien = "Ignacio" (default for this chat_id)
```

#### Scenario 2: Explicit User Mention
```
Chat ID: 807197442 (@bigotesecco)
Message: "Victoria gastó 1500 en taxi"
Result: quien = "Victoria" (mentioned in message)
```

#### Scenario 3: User Alias/Nickname
```
Chat ID: 807197442
Message: "Vicky: 3200 en fruteria"
Result: quien = "Victoria" (Vicky → Victoria mapping)
```

#### Scenario 4: User at End
```
Chat ID: 807197442
Message: "Corte de pelo 1200, Vicky"
Result: quien = "Victoria"
```

---

## 🏗️ Proposed Architecture

### Option A: AI-Based Detection (Recommended)

**Pros:**
- ✅ Flexible (understands natural language)
- ✅ Handles variations ("Victoria", "Vicky", "Vicky gastó", etc.)
- ✅ Can extract from anywhere in message
- ✅ No regex needed

**Cons:**
- ⚠️ Slight increase in prompt complexity
- ⚠️ Depends on AI accuracy

**Implementation:**
1. Update JSON schema to include `quien: string | null`
2. Add user context to prompt (known users and aliases)
3. AI extracts `quien` from message if mentioned
4. Fallback to default user based on chat_id in main.py

### Option B: Regex Pattern Matching

**Pros:**
- ✅ Fast and deterministic
- ✅ No AI cost

**Cons:**
- ❌ Rigid (must match exact patterns)
- ❌ Harder to maintain
- ❌ Miss edge cases

**Decision: Use Option A (AI-Based)**

---

## 📊 Data Structure

### User Configuration

**In main.py:**
```python
# User mapping configuration
USER_CONFIG = {
    # Chat ID → Default user info
    807197442: {
        "default_name": "Ignacio",
        "username": "@bigotesecco",
        "aliases": ["Ignacio", "Nacho", "Igna"]
    },
    641045556: {
        "default_name": "User1",  # To be updated
        "username": None,
        "aliases": ["User1"]
    }
}

# Known users (for AI to detect)
KNOWN_USERS = {
    "Victoria": ["Victoria", "Vicky", "Vicki", "Viki"],
    "Ignacio": ["Ignacio", "Nacho", "Igna", "Nachito"],
    # Add more users as needed
}
```

### Updated JSON Schema

**v2.0 Schema:**
```json
{
  "monto": float,
  "moneda": "USD" | "UYU",
  "categoria": string,
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null
}
```

**v2.1 Schema (fix-username):**
```json
{
  "monto": float,
  "moneda": "USD" | "UYU",
  "categoria": string,
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null,
  "quien": string | null  // NEW! AI extracts if mentioned
}
```

---

## 🔄 Processing Flow

```
1. Message arrives: "Victoria gastó 1500 en taxi"
   Chat ID: 807197442 (@bigotesecco - Ignacio)
   ↓
2. Look up default user: "Ignacio"
   ↓
3. Pass to AI with context:
   - Default user: Ignacio
   - Known users: Victoria (aliases: Vicky, Vicki), Ignacio (aliases: Nacho)
   ↓
4. AI analyzes message:
   - Detects "Victoria" mentioned
   - Returns: quien = "Victoria"
   ↓
5. main.py checks AI result:
   - If quien != null → use AI's value ("Victoria")
   - If quien == null → use default ("Ignacio")
   ↓
6. Save to sheet with correct user: "Victoria"
```

---

## 📝 Prompt Design

### Updated Prompt Section

**Add to SYSTEM_PROMPT:**
```
6. QUIÉN (Usuario que gastó):
   - Si el mensaje menciona explícitamente quién gastó, extrae ese nombre
   - Usuarios conocidos: {known_users_list}
   - Busca patrones como:
     · "Victoria gastó X"
     · "Vicky: X en Y"
     · "Compré X, Vicky"
     · "Para Victoria, X"
   - Si NO se menciona nadie → null (se usa el remitente)
   - Normaliza alias a nombre completo:
     · "Vicky", "Vicki", "Viki" → "Victoria"
     · "Nacho", "Igna" → "Ignacio"

IMPORTANTE: Si el mensaje NO menciona a nadie, devuelve "quien": null
```

**Examples in prompt:**
```
Usuario: "Victoria gastó 1500 en taxi"
{"monto": 1500.0, "moneda": "UYU", "categoria": "transporte", "descripcion": "taxi", "fecha": null, "quien": "Victoria"}

Usuario: "Vicky: 3200 en fruteria"
{"monto": 3200.0, "moneda": "UYU", "categoria": "mercado", "descripcion": "fruteria", "fecha": null, "quien": "Victoria"}

Usuario: "Corte de pelo 1200, Vicky"
{"monto": 1200.0, "moneda": "UYU", "categoria": "belleza", "descripcion": "corte de pelo", "fecha": null, "quien": "Victoria"}

Usuario: "Gasté 500 en café"
{"monto": 500.0, "moneda": "UYU", "categoria": "comida", "descripcion": "café", "fecha": null, "quien": null}
```

---

## 🔧 Implementation Changes

### File 1: main.py

**Current:**
```python
if chat_id == 641045556:
    gasto["quien"] = "User1"
else:
    gasto["quien"] = "User2"
```

**Proposed:**
```python
# User configuration
USER_CONFIG = {
    807197442: {
        "name": "Ignacio",
        "username": "@bigotesecco"
    },
    641045556: {
        "name": "User1",  # Update as needed
        "username": None
    }
}

# Get default user from chat_id
default_user = USER_CONFIG.get(chat_id, {}).get("name", "Unknown")

# AI might have detected a different user in the message
quien = gasto.get("quien")
if quien:
    gasto["quien"] = quien  # Use AI-detected user
else:
    gasto["quien"] = default_user  # Use sender's name
```

### File 2: llm.py

**Add known users context to prompt:**
```python
KNOWN_USERS = {
    "Victoria": ["Victoria", "Vicky", "Vicki", "Viki"],
    "Ignacio": ["Ignacio", "Nacho", "Igna", "Nachito"],
}

def build_prompt(texto, default_user="Unknown"):
    """Build prompt with user context"""
    users_list = ", ".join(KNOWN_USERS.keys())
    aliases_info = "; ".join([
        f"{name} (alias: {', '.join(aliases)})"
        for name, aliases in KNOWN_USERS.items()
    ])
    
    prompt = SYSTEM_PROMPT.format(
        known_users_list=users_list,
        aliases_info=aliases_info,
        default_user=default_user
    )
    
    return prompt + f"\n\nUsuario: {texto}"
```

---

## 🧪 Test Cases

### Test 1: Default User (No Mention)
```
Input: "Gasté 1500 en taxi"
Chat ID: 807197442
Expected: quien = "Ignacio" (default)
```

### Test 2: Explicit Full Name
```
Input: "Victoria gastó 2000 en mercado"
Chat ID: 807197442
Expected: quien = "Victoria" (mentioned)
```

### Test 3: Alias - Beginning
```
Input: "Vicky: 3200 en fruteria"
Chat ID: 807197442
Expected: quien = "Victoria" (Vicky → Victoria)
```

### Test 4: Alias - End
```
Input: "Corte de pelo 1200, Vicky"
Chat ID: 807197442
Expected: quien = "Victoria"
```

### Test 5: Natural Language
```
Input: "Ayer Victoria compró flores por 800"
Chat ID: 807197442
Expected: quien = "Victoria"
```

### Test 6: Context Clue
```
Input: "Para Vicky, Netflix 500"
Chat ID: 807197442
Expected: quien = "Victoria"
```

### Test 7: Self-Reference
```
Input: "Ignacio gastó 1000 en taxi"
Chat ID: 807197442
Expected: quien = "Ignacio" (self-reference OK)
```

### Test 8: Unknown User
```
Input: "Juan gastó 500"
Chat ID: 807197442
Expected: quien = "Ignacio" (fallback to sender, Juan not in KNOWN_USERS)
OR: quien = "Juan" (if we want to allow new users)
```

---

## 🎨 User Experience Examples

### Example 1: Ignacio Logs His Own Expense
```
Ignacio sends: "Gasté 1500 en taxi"

Bot response:
Registrado ✅
$ 1500.0 (UYU)
Categoría: transporte
Descripción: taxi
Fecha: 2025-11-03
Quién: Ignacio ✅

Google Sheet:
2025-11-03 | 1500 | UYU | transporte | taxi | Ignacio
```

### Example 2: Ignacio Logs Victoria's Expense
```
Ignacio sends: "Victoria gastó 2500 en peluquería"

Bot response:
Registrado ✅
$ 2500.0 (UYU)
Categoría: belleza
Descripción: peluquería
Fecha: 2025-11-03
Quién: Victoria ✅

Google Sheet:
2025-11-03 | 2500 | UYU | belleza | peluquería | Victoria
```

### Example 3: Using Nickname
```
Ignacio sends: "Vicky: 3200 fruteria"

Bot response:
Registrado ✅
$ 3200.0 (UYU)
Categoría: mercado
Descripción: fruteria
Fecha: 2025-11-03
Quién: Victoria ✅

Google Sheet:
2025-11-03 | 3200 | UYU | mercado | fruteria | Victoria
```

### Example 4: At the End
```
Ignacio sends: "Corte de pelo 1200, Vicky"

Bot response:
Registrado ✅
$ 1200.0 (UYU)
Categoría: belleza
Descripción: corte de pelo
Fecha: 2025-11-03
Quién: Victoria ✅

Google Sheet:
2025-11-03 | 1200 | UYU | belleza | corte de pelo | Victoria
```

---

## 🔒 Security & Privacy

**Considerations:**
1. Only allow known users (defined in config)
2. Unknown names default to sender
3. Can't spoof other people's expenses (chat_id still tracked)
4. Optional: Log both sender and "quien" for audit trail

**Enhanced Schema (Optional):**
```json
{
  "quien": "Victoria",  // Who spent
  "registrado_por": "Ignacio"  // Who logged it
}
```

This way you can track:
- Who spent the money
- Who registered the expense

---

## 💡 Configuration Design

### Environment Variable Approach
```bash
# In .env
USER_MAPPING='{"807197442": "Ignacio", "641045556": "User1"}'
KNOWN_USERS='{"Victoria": ["Vicky", "Vicki"], "Ignacio": ["Nacho", "Igna"]}'
```

### Code-Based Approach (Simpler)
```python
# In main.py
USER_MAPPING = {
    807197442: "Ignacio",  # @bigotesecco
    641045556: "User1",    # Update this
}

KNOWN_USERS = {
    "Victoria": ["Victoria", "Vicky", "Vicki", "Viki"],
    "Ignacio": ["Ignacio", "Nacho", "Igna", "Nachito"],
}
```

**Recommendation: Code-based** (easier to maintain for 2-3 users)

---

## 🚀 Implementation Strategy

### Phase 1: Update AI Prompt
- Add "quien" to JSON schema
- Add known users context
- Add examples for user detection

### Phase 2: Update main.py
- Define USER_MAPPING and KNOWN_USERS
- Get default user from chat_id
- Check AI result for "quien"
- Use AI's value or default

### Phase 3: Testing
- Test default behavior
- Test explicit mentions
- Test aliases
- Test edge cases

---

## 📋 Backward Compatibility

**Existing data:**
- Has "quien" = "User1" or "User2"
- Will continue to work
- No migration needed

**v2.1 data:**
- Will have actual names (Ignacio, Victoria)
- Easier to read and analyze

---

## 🎯 Success Criteria

**User detection works when:**

1. ✅ Ignacio's expenses show "Ignacio"
2. ✅ "Victoria gastó X" shows "Victoria"
3. ✅ "Vicky: X" shows "Victoria"
4. ✅ "X, Vicky" shows "Victoria"
5. ✅ No mention → shows sender's name
6. ✅ Unknown names → default to sender
7. ✅ Case insensitive ("victoria", "VICTORIA" both work)

---

**Ready to implement!** 🚀


