# 🗺️ Setup Flowchart - Visual Guide

**Follow the arrows → Complete each box → You're done!**

---

## 📊 Complete Setup Flow

```
┌─────────────────────────────────────────────────────────┐
│                    START HERE                           │
│   Do you have all these? Check YES or NO                │
│   • Google account (Gmail)          [  ]               │
│   • Telegram app                    [  ]               │
│   • Docker installed                [  ]               │
│   • Terminal/Command line access    [  ]               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   ALL YES?            │
         └───────┬───────┬───────┘
                 │       │
             YES │       │ NO → Install missing items first
                 │       └─────→ Return when ready
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 1: TELEGRAM BOT (2 min)                         │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Open Telegram                             │    │
│  │ 2. Search "@BotFather"                       │    │
│  │ 3. Send: /newbot                             │    │
│  │ 4. Choose name & username                    │    │
│  │ 5. COPY TOKEN → Save somewhere safe          │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: Bot Token (123456789:ABC...)           [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 1.5: GET CHAT ID (1 min)                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Send "Hello" to your new bot              │    │
│  │ 2. Open browser:                             │    │
│  │    https://api.telegram.org/bot<TOKEN>/      │    │
│  │    getUpdates                                │    │
│  │    (Replace <TOKEN> with your bot token)     │    │
│  │ 3. Find "chat" → "id" number                 │    │
│  │ 4. COPY CHAT ID → Save it                    │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: Your Chat ID (641045556)              [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: GOOGLE GEMINI API (1 min)                    │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Go to: aistudio.google.com/app/apikey     │    │
│  │ 2. Sign in with Google                       │    │
│  │ 3. Click "Create API key"                    │    │
│  │ 4. Choose "new project"                      │    │
│  │ 5. COPY API KEY → Save it                    │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: Gemini API Key (AIzaSy...)            [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 3: GOOGLE SHEET SETUP (2 min)                   │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Go to: sheets.google.com                  │    │
│  │ 2. Create new blank sheet                    │    │
│  │ 3. Rename to "Gastos 2024"                   │    │
│  │ 4. Rename Sheet1 → "registros"               │    │
│  │ 5. Add headers:                              │    │
│  │    A1: Fecha                                 │    │
│  │    B1: Monto                                 │    │
│  │    C1: Categoría                             │    │
│  │    D1: Descripción                           │    │
│  │    E1: Quién                                 │    │
│  │ 6. Copy Sheet ID from URL                    │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: Sheet ID (1a2b3c4d...)                [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 4: SERVICE ACCOUNT (10 min - MOST COMPLEX)      │
│  ┌──────────────────────────────────────────────┐    │
│  │ A. Enable API                                │    │
│  │    1. console.cloud.google.com               │    │
│  │    2. Search "Sheets API"                    │    │
│  │    3. Click "Enable"                         │    │
│  │                                              │    │
│  │ B. Create Service Account                    │    │
│  │    4. Go to "Credentials"                    │    │
│  │    5. Create → Service account               │    │
│  │    6. Name: "expense-bot-writer"             │    │
│  │    7. Create & Continue                      │    │
│  │                                              │    │
│  │ C. Download Key                              │    │
│  │    8. Click on service account               │    │
│  │    9. Keys tab → Add Key → JSON              │    │
│  │   10. JSON file downloads                    │    │
│  │                                              │    │
│  │ D. Share Sheet ⚠️ CRITICAL!                  │    │
│  │   11. Open JSON, copy "client_email"         │    │
│  │   12. Open Google Sheet → Share              │    │
│  │   13. Paste email → Editor → Share           │    │
│  │                                              │    │
│  │ E. Convert to Base64                         │    │
│  │   14. Terminal: base64 -i file.json          │    │
│  │   15. Copy the output                        │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: Base64 string (eyJ0eXBlIjoi...)       [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 5: CREATE .env FILE (2 min)                     │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Terminal: cd Asistente_gastos             │    │
│  │ 2. Create file: nano .env                    │    │
│  │ 3. Paste:                                    │    │
│  │    TELEGRAM_BOT_TOKEN=...                    │    │
│  │    GEMINI_API_KEY=...                        │    │
│  │    GOOGLE_SHEET_ID=...                       │    │
│  │    GOOGLE_CREDENTIALS_JSON_BASE64=...        │    │
│  │ 4. Save: Ctrl+O, Enter, Ctrl+X               │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: .env file created                     [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  STEP 6: TEST LOCALLY (5 min)                         │
│  ┌──────────────────────────────────────────────┐    │
│  │ 1. Build Docker:                             │    │
│  │    docker buildx build --platform            │    │
│  │    linux/amd64 -t asistente-gastos:test .    │    │
│  │                                              │    │
│  │ 2. Run:                                      │    │
│  │    docker run -p 9000:8080 --env-file        │    │
│  │    .env asistente-gastos:test                │    │
│  │                                              │    │
│  │ 3. New terminal, send test:                  │    │
│  │    curl -X POST localhost:9000/...           │    │
│  │                                              │    │
│  │ 4. Check Google Sheet!                       │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  Output: New row in Sheet!                     [  ]  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────────────┐
         │   DID IT WORK?        │
         └───────┬───────┬───────┘
                 │       │
             YES │       │ NO → See Troubleshooting
                 │       └─────→ Check error messages
                 ▼
┌────────────────────────────────────────────────────────┐
│              🎉 SUCCESS! 🎉                            │
│                                                        │
│  You now have a working AI expense tracker!           │
│                                                        │
│  Next Steps:                                          │
│  • Test with real Telegram messages                   │
│  • Deploy to AWS Lambda (optional)                    │
│  • Customize categories                               │
│  • Add more users                                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🔄 Parallel vs Sequential Steps

Some steps can be done in parallel to save time!

### ⚡ Fast Track (20 min)

```
Do simultaneously:
├─ Browser Tab 1: Create Telegram Bot
├─ Browser Tab 2: Get Gemini API Key  
└─ Browser Tab 3: Create Google Sheet

Then do sequentially:
└─ Service Account setup (requires focus)
   └─ Create .env file
      └─ Test locally
```

---

## 🎯 Checkpoint System

After each step, verify:

### Checkpoint 1 (After Steps 1-3)
```
You should have:
✓ Telegram bot token
✓ Your chat ID
✓ Gemini API key
✓ Google Sheet ID

Total items: 4
Time spent: ~5 minutes
```

### Checkpoint 2 (After Step 4)
```
You should have:
✓ Everything from Checkpoint 1
✓ Service account email
✓ JSON key file downloaded
✓ Sheet shared with service account
✓ Base64 encoded credentials

Total items: 9
Time spent: ~15 minutes
```

### Checkpoint 3 (After Step 5)
```
You should have:
✓ Everything from Checkpoint 2
✓ .env file created
✓ All 4 environment variables set
✓ File is gitignored

Total items: 12
Time spent: ~17 minutes
```

### Final Checkpoint (After Step 6)
```
You should have:
✓ Everything from Checkpoint 3
✓ Docker image built
✓ Container running
✓ Test message sent
✓ NEW ROW IN GOOGLE SHEET! 🎉

Total items: 17
Time spent: ~22 minutes
Status: COMPLETE!
```

---

## 🚦 Traffic Light System

Use this to track your progress:

| Step | Status | Time | Issues? |
|------|--------|------|---------|
| 1. Telegram Bot | 🔴 🟡 🟢 | ___ min | _______ |
| 2. Gemini API | 🔴 🟡 🟢 | ___ min | _______ |
| 3. Google Sheet | 🔴 🟡 🟢 | ___ min | _______ |
| 4. Service Account | 🔴 🟡 🟢 | ___ min | _______ |
| 5. .env File | 🔴 🟡 🟢 | ___ min | _______ |
| 6. Local Test | 🔴 🟡 🟢 | ___ min | _______ |

Legend:
- 🔴 Not started / Blocked
- 🟡 In progress / Issues
- 🟢 Complete / Working

---

## 🆘 Decision Tree for Troubleshooting

```
Error occurred?
│
├─ Yes → What type?
│         │
│         ├─ Telegram related
│         │   └─ Check: Token format, Chat ID correct?
│         │
│         ├─ Gemini API related
│         │   └─ Check: API key valid, has quota?
│         │
│         ├─ Google Sheets related
│         │   └─ Check: Sheet shared with service account?
│         │
│         ├─ Docker related
│         │   └─ Check: Platform flag, .env file exists?
│         │
│         └─ Unknown error
│             └─ Check logs: docker logs <container_id>
│
└─ No → Proceed to next step! ✅
```

---

## 📱 Mobile-Friendly Quick Reference

**Minimum screen screenshot checklist:**

When you see these screens, you're on the right track:

1. ✅ BotFather confirmation message
2. ✅ Gemini API key displayed
3. ✅ Google Sheet with headers
4. ✅ Service account JSON download
5. ✅ Terminal showing "ok" response
6. ✅ New row in Google Sheet

**Take screenshots of all these!** They prove you did it right.

---

**Total Time: ~20-30 minutes**  
**Difficulty: Easy** (just follow the arrows!)  
**Success Rate: 95%+** (if you follow each step carefully)


