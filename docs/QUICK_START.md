# ⚡ Quick Start Guide - 15 Minutes to Working Bot

**For people who just want it working NOW!**

---

## 📋 Pre-Flight Checklist

You need:
- [ ] Google account (Gmail)
- [ ] Telegram app
- [ ] Terminal access
- [ ] Docker installed

---

## 🚀 5-Step Express Setup

### 1️⃣ TELEGRAM (2 min)

```
1. Open Telegram → Search "@BotFather"
2. Send: /newbot
3. Name: "My Expense Bot"
4. Username: "my_expense_2024_bot"
5. COPY THE TOKEN → Save it!
```

Get your chat ID:
```
1. Send "Hello" to your new bot
2. Open: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
3. Copy the "chat" "id" number
```

---

### 2️⃣ GOOGLE GEMINI (1 min)

```
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API key in new project"
3. COPY THE KEY → Save it!
```

---

### 3️⃣ GOOGLE SHEETS (2 min)

```
1. Go to: https://sheets.google.com
2. Create new sheet → Name it "Gastos 2024"
3. Rename Sheet1 → "registros"
4. Add headers: Fecha | Monto | Categoría | Descripción | Quién
5. Copy Sheet ID from URL (between /d/ and /edit)
```

---

### 4️⃣ SERVICE ACCOUNT (5 min)

```
1. Go to: https://console.cloud.google.com
2. Search "Sheets API" → Enable it
3. Credentials → Create credentials → Service account
4. Name: "expense-bot" → Create
5. Click on it → Keys → Add Key → JSON → Download
6. Open the JSON → Copy "client_email"
7. Go to your Google Sheet → Share with that email → Editor
```

Convert to base64:
```bash
cd /Users/isecco/Code/Asistente_gastos
base64 -i ~/Downloads/your-project-*.json | tr -d '\n' > google_sa_base64.txt
```

---

### 5️⃣ CREATE .env FILE (2 min)

```bash
cd /Users/isecco/Code/Asistente_gastos
nano .env
```

Paste (with YOUR values):
```
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_gemini_key_here
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_JSON_BASE64=paste_the_base64_here
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## ✅ TEST IT NOW!

```bash
# Build
docker buildx build --platform linux/amd64 -t asistente-gastos:test .

# Run
docker run -p 9000:8080 --env-file .env asistente-gastos:test
```

In NEW terminal:
```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"gasté 20000 en comida\",\"chat\":{\"id\":YOUR_CHAT_ID}}}"}'
```

**Check your Google Sheet** → You should see a new row! 🎉

---

## 🆘 Not Working?

**Error: "404 Not Found" getting chat ID**
→ Add `bot` before your token: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`

**Error: "Can't access sheet"**
→ Did you share the Sheet with the service account email?

**Error: "Invalid API key"**
→ Check you copied the full Gemini API key (starts with `AIzaSy`)

**Error: "Telegram token invalid"**
→ Check the token format: `123456789:ABC...` (numbers:letters)

**Error: "Module not found"**
→ Rebuild: `docker buildx build --no-cache --platform linux/amd64 -t asistente-gastos:test .`

---

## 📚 Want More Details?

Read the full guide: `SETUP_GUIDE.md`

**Ready to deploy to AWS?** See `README.md` deployment section.

---

**That's it! You now have an AI expense tracker! 🚀**

Test it by sending messages to your Telegram bot:
- "Gasté 15000 en taxi"
- "Pagué 45000 en mercado"
- "Comí empanadas por 8000"

All expenses will appear in your Google Sheet automatically! 📊

