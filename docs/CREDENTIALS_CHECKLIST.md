# ✅ Credentials Checklist

**Use this to track your setup progress**

---

## 📋 Credential Collection Status

### 1. Telegram Bot
- [ ] Created bot with @BotFather
- [ ] Bot Username: `___________________________`
- [ ] Bot Token obtained: `___________________________`
- [ ] Sent "Hello" to bot
- [ ] Chat ID obtained: `___________________________`

**Token format check:** Should be `123456789:ABC...` (numbers:letters)

---

### 2. Google Gemini
- [ ] Visited https://aistudio.google.com/app/apikey
- [ ] Created API key
- [ ] API Key: `___________________________`
- [ ] Tested with curl (optional but recommended)

**Key format check:** Should start with `AIzaSy...`

---

### 3. Google Sheets
- [ ] Created new Google Sheet
- [ ] Sheet Name: `___________________________`
- [ ] Renamed first sheet to "registros"
- [ ] Added headers (Fecha, Monto, Categoría, Descripción, Quién)
- [ ] Sheet ID: `___________________________`
- [ ] Sheet URL: `___________________________`

**ID location:** Between `/d/` and `/edit` in URL

---

### 4. Google Service Account
- [ ] Enabled Google Sheets API
- [ ] Created service account named "expense-bot-writer"
- [ ] Downloaded JSON key file
- [ ] Service Account Email: `___________________________`
- [ ] Shared Google Sheet with service account (as Editor)
- [ ] JSON saved to: `/Users/isecco/Code/Asistente_gastos/google_sa.json`
- [ ] Converted to base64
- [ ] Base64 saved to: `google_sa_base64.txt`

**Critical:** Did you share the sheet? This is the #1 cause of errors!

---

### 5. Environment Setup
- [ ] Created `.env` file in project root
- [ ] Added TELEGRAM_BOT_TOKEN
- [ ] Added GEMINI_API_KEY
- [ ] Added GOOGLE_SHEET_ID
- [ ] Added GOOGLE_CREDENTIALS_JSON_BASE64
- [ ] Verified `.env` is in `.gitignore`
- [ ] Verified `google_sa.json` is in `.gitignore`

---

### 6. Local Testing
- [ ] Docker installed and running
- [ ] Built Docker image: `docker buildx build ...`
- [ ] Started container: `docker run ...`
- [ ] Sent test request with curl
- [ ] Verified row appeared in Google Sheet
- [ ] Stopped container

---

### 7. AWS Setup (Optional - for deployment)
- [ ] Created AWS account
- [ ] Selected region: `___________________________`
- [ ] Created ECR repository "asistente-gastos"
- [ ] ECR URI: `___________________________`
- [ ] Created IAM user for deployment
- [ ] AWS Access Key ID: `___________________________`
- [ ] AWS Secret Access Key: `___________________________`
- [ ] Configured AWS CLI: `aws configure`

---

## 🔒 Security Checklist

Before considering yourself "done", verify:

- [ ] `.env` file is NOT committed to git
- [ ] `google_sa.json` is NOT committed to git
- [ ] `google_sa_base64.txt` is NOT committed to git
- [ ] All credentials are backed up securely (password manager, encrypted file, etc.)
- [ ] You understand NOT to share these credentials publicly
- [ ] API keys are stored only in environment variables, not in code

---

## 📝 Your Credentials (Fill this out, then KEEP IT SAFE!)

```
===========================================
  ASISTENTE DE GASTOS - MY CREDENTIALS
===========================================

TELEGRAM
--------
Bot Username: @___________________________
Token: ___________________________
My Chat ID: ___________________________

GOOGLE GEMINI
-------------
API Key: ___________________________

GOOGLE SHEETS
-------------
Sheet Name: ___________________________
Sheet ID: ___________________________

GOOGLE SERVICE ACCOUNT
----------------------
Email: ___________________________@___.iam.gserviceaccount.com
Base64 Location: /Users/isecco/Code/Asistente_gastos/google_sa_base64.txt

AWS (if deploying)
------------------
Account ID: ___________________________
Region: ___________________________
ECR URI: ___________________________
Access Key ID: ___________________________
Secret Key: [STORED IN AWS CLI CONFIG]

===========================================
Created: _______________
Last Updated: _______________
===========================================
```

**⚠️ Save this file OUTSIDE of git!** Suggested location:
- Password manager (1Password, LastPass, etc.)
- Encrypted notes app
- Secure cloud storage (with encryption)
- Physical notebook (old school but secure!)

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| "404 Not Found" on getUpdates | Add `bot` prefix: `api.telegram.org/bot<TOKEN>/getUpdates` |
| "Permission denied" on Sheet | Share Sheet with service account email |
| "Invalid API key" | Check you copied full key, no spaces |
| "Telegram token invalid" | Check format: `123456789:ABC...` |
| "Can't find chat ID" | Send message to bot first, then check getUpdates |
| "Module not found in Docker" | Rebuild with `--no-cache` flag |

---

## ✅ Final Verification

Run this test command to verify everything works:

```bash
cd /Users/isecco/Code/Asistente_gastos

# Build
docker buildx build --platform linux/amd64 -t asistente-gastos:test .

# Run  
docker run -p 9000:8080 --env-file .env asistente-gastos:test
```

In another terminal:
```bash
# Replace YOUR_CHAT_ID with your actual chat ID!
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"body":"{\"message\":{\"text\":\"gasté 99999 en prueba\",\"chat\":{\"id\":YOUR_CHAT_ID}}}"}'
```

**If you see a new row in your Google Sheet with "99999" → SUCCESS! 🎉**

---

**Total time to complete:** ~30 minutes  
**Difficulty:** Easy (just follow the steps)  
**Cost:** $0 (all free tiers)  
**Coolness factor:** 🔥🔥🔥🔥🔥


