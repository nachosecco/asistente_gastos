# 🚀 Asistente de Gastos - Complete Setup Guide

**Time Required:** ~30 minutes  
**Cost:** $0 (everything uses free tiers)  
**Difficulty:** Easy - just follow the steps!

---

## 📋 What You'll Need

By the end of this guide, you'll have:
- ✅ Telegram Bot created and token obtained
- ✅ Google Gemini API key
- ✅ Google Sheets created and configured
- ✅ Google Service Account with credentials
- ✅ AWS account ready for Lambda deployment
- ✅ Local environment configured for testing

---

# STEP 1: Create Telegram Bot (5 minutes)

## 1.1 Open Telegram and Find BotFather

1. Open Telegram on your phone or desktop
2. In the search bar, type: `@BotFather`
3. Click on the official BotFather bot (verified with blue checkmark)
4. Click **START**

## 1.2 Create Your Bot

1. Send this command to BotFather:
   ```
   /newbot
   ```

2. BotFather will ask: **"Alright, a new bot. How are we going to call it?"**
   - Type a friendly name (e.g., `My Expense Assistant`)
   - This is just a display name, it can be anything

3. BotFather will ask: **"Now, let's choose a username for your bot."**
   - Type a unique username ending in `bot` (e.g., `my_expense_tracker_bot`)
   - This must be unique across all Telegram
   - If taken, try adding numbers (e.g., `my_expense_tracker_2024_bot`)

4. **SUCCESS!** BotFather will reply with:
   ```
   Done! Congratulations on your new bot.
   You will find it at t.me/your_bot_username
   
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklmnoPQRsTUVwxyZ
   ```

## 1.3 Save Your Token

**COPY THIS TOKEN IMMEDIATELY!**

Create a temporary file to save all credentials:
```bash
# Create credentials file
nano ~/asistente-gastos-credentials.txt
```

Paste this format:
```
=== TELEGRAM ===
Bot Username: @your_bot_username
Token: 123456789:ABCdefGHIjklmnoPQRsTUVwxyZ
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

## 1.4 Get Your Chat ID

1. Open your new bot in Telegram (click the link BotFather gave you)
2. Click **START**
3. Send any message to your bot (e.g., "Hello")
4. Open this URL in your browser (replace YOUR_TOKEN with your actual token):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   
   **Example:** If your token is `123456789:ABCdefGHI`, the URL would be:
   ```
   https://api.telegram.org/bot123456789:ABCdefGHI/getUpdates
   ```
   
   ⚠️ **Important:** Don't forget the `bot` prefix before your token!
   
5. You'll see JSON like this:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": 641045556,  ← THIS IS YOUR CHAT ID
           "first_name": "Your Name"
         }
       }
     }]
   }
   ```

6. **Copy your Chat ID** and add it to your credentials file:
   ```
   Chat ID: 641045556
   ```

**✅ STEP 1 COMPLETE!** You have your Telegram bot ready.

---

# STEP 2: Get Google Gemini API Key (3 minutes)

## 2.1 Go to Google AI Studio

1. Open your browser and go to:
   ```
   https://aistudio.google.com/app/apikey
   ```

2. **Sign in** with your Google account
   - Use any Gmail account (personal is fine)

## 2.2 Create API Key

1. Click the blue button: **"Get API key"** or **"Create API key"**

2. You'll see a modal with options:
   - Click **"Create API key in new project"**
   - OR select an existing Google Cloud project if you have one

3. **COPY YOUR API KEY IMMEDIATELY!**
   - It looks like: `AIzaSyABcDeFgHiJkLmNoPqRsTuVwXyZ123456`
   - You can only see it once!

4. Add to your credentials file:
   ```
   === GOOGLE GEMINI ===
   API Key: AIzaSyABcDeFgHiJkLmNoPqRsTuVwXyZ123456
   ```

## 2.3 Verify It Works

Test in terminal:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=<GEMINI_API_KEY>" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

If you see JSON response with "Hello" reply → **IT WORKS!** ✅

**⚠️ IMPORTANT:** Keep this key secret! Never commit it to GitHub!

**✅ STEP 2 COMPLETE!** You have Gemini AI access.

---

# STEP 3: Create Google Sheet (2 minutes)

## 3.1 Create New Spreadsheet

1. Go to: https://sheets.google.com
2. Click **"+ Blank"** to create new spreadsheet
3. **Rename it** to: `Gastos 2024` (or any name you prefer)

## 3.2 Set Up the Sheet Structure

1. **Rename the first sheet:**
   - Right-click on "Sheet1" tab at bottom
   - Click "Rename"
   - Change to: `registros`

2. **Add column headers** in the first row:
   - A1: `Fecha`
   - B1: `Monto`
   - C1: `Categoría`
   - D1: `Descripción`
   - E1: `Quién`

3. **Optional: Format it nicely**
   - Select row 1 (header row)
   - Make it **bold** (Ctrl+B)
   - Add background color (click paint bucket icon)
   - Freeze header: View → Freeze → 1 row

## 3.3 Get Sheet ID

1. Look at the URL in your browser:
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
                                        ^^^^^^^^^^^^^^^^^^
                                        THIS IS YOUR SHEET ID
   ```

2. **Copy the Sheet ID** (the long string between `/d/` and `/edit`)

3. Add to credentials file:
   ```
   === GOOGLE SHEETS ===
   Sheet Name: Gastos 2024
   Sheet ID: 1a2b3c4d5e6f7g8h9i0j
   Sheet URL: [paste full URL]
   ```

**✅ STEP 3 COMPLETE!** Your expense sheet is ready.

---

# STEP 4: Create Google Service Account (10 minutes)

This is the most complex step, but I'll make it simple!

## 4.1 Go to Google Cloud Console

1. Open: https://console.cloud.google.com
2. Sign in with the same Google account you used for Gemini

## 4.2 Create or Select Project

**If you used "Create API key in new project" in Step 2:**
1. Click the project dropdown (top left, next to "Google Cloud")
2. You'll see a project like "My Project 12345" or "Gemini API Project"
3. Click to select it

**If you need to create a new project:**
1. Click project dropdown → "NEW PROJECT"
2. Name: `Asistente Gastos`
3. Click "CREATE"
4. Wait 10 seconds, then select it from dropdown

## 4.3 Enable Google Sheets API

1. In the search bar at top, type: `Sheets API`
2. Click **"Google Sheets API"**
3. Click the blue **"ENABLE"** button
4. Wait for it to enable (~5 seconds)

## 4.4 Create Service Account

1. In the left sidebar, click **"Credentials"**
   - Or search for "Credentials" in the top search bar

2. Click **"+ CREATE CREDENTIALS"** at the top

3. Select **"Service account"**

4. Fill in the form:
   - **Service account name:** `expense-bot-writer`
   - **Service account ID:** (auto-filled, leave it)
   - **Description:** `Bot for writing expenses to Google Sheets`
   - Click **"CREATE AND CONTINUE"**

5. **Grant access (Optional):**
   - Click **"CONTINUE"** (you can skip this)

6. **Grant users access (Optional):**
   - Click **"DONE"** (skip this too)

## 4.5 Create Service Account Key

1. You'll see your new service account in the list
2. Click on it (the email like `expense-bot-writer@project-123456.iam.gserviceaccount.com`)

3. Go to the **"KEYS"** tab at the top

4. Click **"ADD KEY"** → **"Create new key"**

5. Select **"JSON"** format

6. Click **"CREATE"**

7. **A JSON file will download automatically!**
   - File name like: `project-123456-abc123def456.json`
   - **SAVE THIS FILE SECURELY!**
   - Move it to your project folder:
     ```bash
     mv ~/Downloads/project-*.json /Users/isecco/Code/Asistente_gastos/google_sa.json
     ```

## 4.6 Share Sheet with Service Account

**CRITICAL STEP - Don't skip!**

1. Open the JSON file you just downloaded
2. Find the `client_email` field (looks like):
   ```json
   "client_email": "expense-bot-writer@project-123456.iam.gserviceaccount.com"
   ```
3. **Copy this email address**

4. Go back to your Google Sheet (from Step 3)
5. Click the **"Share"** button (top right)
6. **Paste the service account email**
7. Set permission to **"Editor"**
8. **UNCHECK** "Notify people" (it's a bot, not a person!)
9. Click **"Send"** or **"Share"**

**✅ CRITICAL:** If you don't do this, the bot can't write to your sheet!

## 4.7 Convert Credentials to Base64

The Lambda needs credentials as a base64-encoded string:

```bash
# Navigate to project folder
cd /Users/isecco/Code/Asistente_gastos

# Convert JSON to base64
base64 -i google_sa.json | tr -d '\n' > google_sa_base64.txt

# Display it
cat google_sa_base64.txt
```

**Copy the entire base64 string** and add to credentials file:
```
=== SERVICE ACCOUNT ===
Email: expense-bot-writer@project-123456.iam.gserviceaccount.com
JSON File: google_sa.json (stored locally)
Base64: eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6Im15LXByb2plY3... [LONG STRING]
```

**✅ STEP 4 COMPLETE!** Google authentication is configured.

---

# STEP 5: Set Up Local Environment (5 minutes)

## 5.1 Create .env File

```bash
# Navigate to project
cd /Users/isecco/Code/Asistente_gastos

# Create .env file
nano .env
```

Paste this (replace with YOUR values):
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRsTUVwxyZ

# Google Gemini AI
GEMINI_API_KEY=AIzaSyABcDeFgHiJkLmNoPqRsTuVwXyZ123456

# Google Sheets
GOOGLE_SHEET_ID=1a2b3c4d5e6f7g8h9i0j
GOOGLE_CREDENTIALS_JSON_BASE64=eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6Im15LXByb2plY3...
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

## 5.2 Verify .gitignore

Make sure `.env` and `google_sa.json` are in `.gitignore`:

```bash
# Check if they're already ignored
grep -E '\.env|google_sa\.json' .gitignore
```

If not found, add them:
```bash
echo ".env" >> .gitignore
echo "google_sa.json" >> .gitignore
echo "google_sa_base64.txt" >> .gitignore
```

**✅ STEP 5 COMPLETE!** Local environment is ready.

---

# STEP 6: Test Locally with Docker (5 minutes)

## 6.1 Build Docker Image

```bash
cd /Users/isecco/Code/Asistente_gastos

# Build for local testing
docker buildx build --platform linux/amd64 -t asistente-gastos:test .
```

## 6.2 Run Locally

```bash
# Run with environment variables
docker run -p 9000:8080 --env-file .env asistente-gastos:test
```

You should see:
```
START RequestId: ...
Listening on port 8080
```

## 6.3 Test with Curl

Open a NEW terminal and run:

```bash
# Test message
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "{\"message\":{\"text\":\"gasté 25000 en almuerzo\",\"chat\":{\"id\":641045556}}}"
  }'
```

**Expected response:**
```json
{"statusCode": 200, "body": "ok"}
```

## 6.4 Check Google Sheet

1. Open your Google Sheet
2. You should see a new row:
   ```
   2024-11-02 | 25000 | comida | almuerzo | User1
   ```

**🎉 IF YOU SEE THIS → IT WORKS LOCALLY!** ✅

If not, check the Docker logs for errors.

Stop Docker with `Ctrl+C`.

**✅ STEP 6 COMPLETE!** Local testing successful.

---

# STEP 7: AWS Account Setup (Optional - for deployment)

**Note:** This step is only needed if you want to deploy to AWS Lambda. You can skip this and use the local version for now.

## 7.1 Create AWS Account

1. Go to: https://aws.amazon.com
2. Click **"Create an AWS Account"**
3. Follow the signup process:
   - Email address
   - Password
   - Account name: `Personal` or your name
   - Contact information
   - **Credit card required** (but won't be charged for free tier usage)
   - Phone verification
   - Choose "Basic Support - Free"

## 7.2 Sign in to AWS Console

1. Go to: https://console.aws.amazon.com
2. Sign in with your new account

## 7.3 Set Region

1. Look at top-right corner (next to your account name)
2. Click the region dropdown
3. Select: **"São Paulo (sa-east-1)"** (closest to you, or choose any)

## 7.4 Create ECR Repository

1. Search for "ECR" in the top search bar
2. Click **"Elastic Container Registry"**
3. Click **"Get Started"** or **"Create repository"**
4. Settings:
   - **Visibility:** Private
   - **Repository name:** `asistente-gastos`
   - Leave other settings default
5. Click **"Create repository"**
6. **Copy the URI** (looks like: `123456789.dkr.ecr.sa-east-1.amazonaws.com/asistente-gastos`)

## 7.5 Configure AWS CLI

```bash
# Install AWS CLI (if not installed)
# macOS:
brew install awscli

# Configure credentials
aws configure

# You'll be asked:
# AWS Access Key ID: [Create in IAM → Users → Security credentials]
# AWS Secret Access Key: [From same place]
# Default region name: sa-east-1
# Default output format: json
```

**Creating Access Keys:**
1. In AWS Console, search for "IAM"
2. Click "Users" → "Add users"
3. Username: `asistente-gastos-deployer`
4. Check "Access key - Programmatic access"
5. Permissions: "AdministratorAccess" (for simplicity, restrict later)
6. Create user
7. **COPY AND SAVE** Access Key ID and Secret Access Key

**✅ STEP 7 COMPLETE!** AWS is ready for deployment.

---

# 📝 Summary - Your Credentials

Save this file securely (NOT in git):

```
===========================================
  ASISTENTE DE GASTOS - CREDENTIALS
===========================================

TELEGRAM BOT
------------
Bot Username: @your_bot_username
Token: 123456789:ABCdefGHIjklmnoPQRsTUVwxyZ
Your Chat ID: 641045556

GOOGLE GEMINI
-------------
API Key: AIzaSyABcDeFgHiJkLmNoPqRsTuVwXyZ123456

GOOGLE SHEETS
-------------
Sheet Name: Gastos 2024
Sheet ID: 1a2b3c4d5e6f7g8h9i0j
Sheet URL: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit

GOOGLE SERVICE ACCOUNT
----------------------
Email: expense-bot-writer@project-123456.iam.gserviceaccount.com
JSON File Location: /Users/isecco/Code/Asistente_gastos/google_sa.json
Base64: [VERY LONG STRING]

AWS (Optional)
--------------
Account ID: 123456789012
Region: sa-east-1
ECR URI: 123456789.dkr.ecr.sa-east-1.amazonaws.com/asistente-gastos
Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

===========================================
  ⚠️ KEEP THIS FILE SECURE AND PRIVATE!
===========================================
```

---

# 🎯 Next Steps

## Option A: Use Locally (No AWS needed)

```bash
# Start the bot
docker run -p 9000:8080 --env-file .env asistente-gastos:test

# In another terminal, create a simple webhook receiver
# (or just test with curl as shown above)
```

## Option B: Deploy to AWS Lambda

Follow the deployment instructions in the README.md:
1. Build for ARM64: `docker buildx build --platform linux/amd64 ...`
2. Push to ECR
3. Create Lambda function
4. Set up webhook with Telegram

---

# 🆘 Troubleshooting

## Issue: "404 Not Found" when accessing Telegram getUpdates

**Solution:** Make sure you include the `bot` prefix before your token!

❌ **WRONG:**
```
https://api.telegram.org/8085599904:AAGi2v.../getUpdates
```

✅ **CORRECT:**
```
https://api.telegram.org/bot8085599904:AAGi2v.../getUpdates
                        ^^^
                    Don't forget "bot"!
```

The Telegram Bot API **requires** the word `bot` before your token in all API calls.

## Issue: "Can't write to Google Sheets"

**Solution:** Make sure you shared the Sheet with the service account email!
1. Open Google Sheet
2. Click "Share"
3. Add: `expense-bot-writer@project-123456.iam.gserviceaccount.com`
4. Permission: Editor

## Issue: "Gemini API error"

**Solution:** Check your API key is correct and has free quota:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```

## Issue: "Docker build fails"

**Solution:** Make sure you're on the correct platform:
```bash
docker buildx build --platform linux/amd64 -t asistente-gastos:test .
```

## Issue: "Module not found errors"

**Solution:** Rebuild with no cache:
```bash
docker buildx build --no-cache --platform linux/amd64 -t asistente-gastos:test .
```

---

# ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] Telegram bot responds to /start command
- [ ] Gemini API key works (curl test passes)
- [ ] Google Sheet exists with correct headers
- [ ] Service account email is shared with Sheet
- [ ] .env file contains all 4 credentials
- [ ] Docker image builds successfully
- [ ] Local test writes to Google Sheet
- [ ] You saved all credentials securely

---

**🎉 CONGRATULATIONS!** You're ready to track expenses with AI!

**Test it for real:**
1. Send a message to your Telegram bot: `Gasté 15000 en taxi`
2. Check your Google Sheet for the new entry
3. Profit! 💰


