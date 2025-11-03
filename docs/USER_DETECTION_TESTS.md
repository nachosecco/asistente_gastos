# 🧪 User Detection - Test Cases

**Branch:** `fix-username`  
**Feature:** Smart detection of Ignacio vs Victoria

---

## 📋 Test Plan

### Rule Summary
- **If message mentions:** Victoria, Vicky, Vicki, or Viki → `quien = "Victoria"`
- **Otherwise:** → `quien = "Ignacio"` (default)

---

## ✅ Test Cases

### Category 1: Default User (Ignacio)

#### Test 1.1: No user mentioned
```
Input: "Gasté 1500 en taxi"
Expected Output:
  quien: "Ignacio"
  categoria: "transporte"
  moneda: "UYU"
```

#### Test 1.2: First person ("Pagué", "Gasté", "Compré")
```
Input: "Pagué 50 dólares en Amazon"
Expected Output:
  quien: "Ignacio"
  moneda: "USD"
  categoria: "tecnologia"
```

#### Test 1.3: Just amount and item
```
Input: "Almuerzo 800"
Expected Output:
  quien: "Ignacio"
  categoria: "comida"
```

---

### Category 2: Victoria - Full Name

#### Test 2.1: "Victoria gastó"
```
Input: "Victoria gastó 2000 en mercado"
Expected Output:
  quien: "Victoria"
  monto: 2000.0
  categoria: "mercado"
```

#### Test 2.2: "Ayer Victoria"
```
Input: "Ayer Victoria compró flores 800"
Expected Output:
  quien: "Victoria"
  fecha: "2025-11-02" (yesterday)
  categoria: "regalos"
```

#### Test 2.3: "Para Victoria"
```
Input: "Para Victoria, Netflix 500"
Expected Output:
  quien: "Victoria"
  categoria: "suscripciones"
```

---

### Category 3: Victoria - Alias "Vicky"

#### Test 3.1: "Vicky:" prefix
```
Input: "Vicky: 3200 en fruteria"
Expected Output:
  quien: "Victoria"
  monto: 3200.0
  categoria: "mercado"
```

#### Test 3.2: "Vicky" at end
```
Input: "Corte de pelo 1200, Vicky"
Expected Output:
  quien: "Victoria"
  monto: 1200.0
  categoria: "belleza"
```

#### Test 3.3: "Vicky gastó"
```
Input: "Vicky gastó 500 en taxi"
Expected Output:
  quien: "Victoria"
  categoria: "transporte"
```

---

### Category 4: Victoria - Other Aliases

#### Test 4.1: "Vicki"
```
Input: "Vicki pagó 25 u$s en Spotify"
Expected Output:
  quien: "Victoria"
  moneda: "USD"
  categoria: "suscripciones"
```

#### Test 4.2: "Viki"
```
Input: "Ayer Viki gastó 1500"
Expected Output:
  quien: "Victoria"
  fecha: "2025-11-02"
```

---

### Category 5: Mixed Scenarios

#### Test 5.1: Victoria with USD
```
Input: "Victoria: 75 dólares en ropa"
Expected Output:
  quien: "Victoria"
  moneda: "USD"
  categoria: "ropa"
```

#### Test 5.2: Ignacio (explicit)
```
Input: "Ignacio pagó la luz 3000"
Expected Output:
  quien: "Ignacio"
  categoria: "servicios domesticos"
```

#### Test 5.3: Case insensitive
```
Input: "VICKY gastó 100"
Expected Output:
  quien: "Victoria"
```

---

## 🧪 Test Commands (Local Docker)

```bash
# Build and run v2.1 with user detection
cd /Users/isecco/Code/Asistente_gastos
git checkout fix-username
docker buildx build --platform linux/amd64 -t asistente-gastos:v2.1 .
docker run -p 9000:8080 --env-file .env asistente-gastos:v2.1
```

**In new terminal, run each test:**

### Test Ignacio (default)
```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"gasté 1500 en taxi\",\"chat\":{\"id\":807197442}}}"}'
```
**Check Sheet:** quien = Ignacio ✅

### Test Victoria (full name)
```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"Victoria gastó 2000 en mercado\",\"chat\":{\"id\":807197442}}}"}'
```
**Check Sheet:** quien = Victoria ✅

### Test Vicky (alias)
```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"Vicky: 3200 en fruteria\",\"chat\":{\"id\":807197442}}}"}'
```
**Check Sheet:** quien = Victoria ✅

### Test at end
```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"Corte de pelo 1200, Vicky\",\"chat\":{\"id\":807197442}}}"}'
```
**Check Sheet:** quien = Victoria ✅

---

## 📊 Expected Results

**Your Google Sheet should show:**

| Fecha | Monto | Moneda | Categoría | Descripción | Quién |
|-------|-------|--------|-----------|-------------|-------|
| 2025-11-03 | 1500 | UYU | transporte | taxi | **Ignacio** |
| 2025-11-03 | 2000 | UYU | mercado | mercado | **Victoria** |
| 2025-11-03 | 3200 | UYU | mercado | fruteria | **Victoria** |
| 2025-11-03 | 1200 | UYU | belleza | corte de pelo | **Victoria** |

---

## 🎯 Success Criteria

**User detection works correctly when:**

- [ ] "Gasté X" → Ignacio
- [ ] "Pagué X" → Ignacio
- [ ] "Compré X" → Ignacio
- [ ] "Victoria gastó X" → Victoria
- [ ] "Vicky: X" → Victoria
- [ ] "X, Vicky" → Victoria
- [ ] "Vicki pagó X" → Victoria
- [ ] "Viki gastó X" → Victoria
- [ ] All variations of Victoria → Victoria
- [ ] Everything else → Ignacio

---

## 🚀 Ready to Merge and Deploy

Once all tests pass:

```bash
# Merge to main
git checkout main
git merge fix-username -m "Merge fix-username: Smart user detection Ignacio/Victoria"

# Deploy to AWS
# (follow deployment commands from previous guides)
```

---

**Total Test Cases:** 15  
**Expected Pass Rate:** 100%  
**Time to Test:** ~10 minutes


