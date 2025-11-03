# 📱 Telegram Bot API - Quick Reference

**Official Documentation:** https://core.telegram.org/bots/api

---

## ✅ Correct URL Format

All Telegram Bot API calls must include the `bot` prefix before your token:

```
https://api.telegram.org/bot<TOKEN>/<METHOD>
                          ^^^
                   ALWAYS include "bot"!
```

---

## 🔑 Common Methods You'll Use

### 1. Get Updates (Get Chat ID)

**Purpose:** Retrieve messages sent to your bot (including getting your chat ID)

**URL Format:**
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

**Example:**
```
https://api.telegram.org/bot123456789:ABCdefGHIjklmnoPQRsTUVwxyZ/getUpdates
```

**Response (JSON):**
```json
{
  "ok": true,
  "result": [{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "from": {
        "id": 641045556,  ← YOUR CHAT ID
        "is_bot": false,
        "first_name": "Your Name"
      },
      "chat": {
        "id": 641045556,  ← YOUR CHAT ID (same as above)
        "first_name": "Your Name",
        "type": "private"
      },
      "date": 1699999999,
      "text": "Hello"
    }
  }]
}
```

---

### 2. Send Message

**Purpose:** Send a message to a user/chat

**URL Format:**
```
https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage
```

**Method:** POST

**Body (JSON):**
```json
{
  "chat_id": 641045556,
  "text": "Your message here"
}
```

**Example with curl:**
```bash
curl -X POST "https://api.telegram.org/bot123456789:ABC.../sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 641045556, "text": "Hello from bot!"}'
```

---

### 3. Set Webhook

**Purpose:** Configure where Telegram should send updates

**URL Format:**
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook
```

**Method:** POST

**Parameters:**
- `url`: Your webhook endpoint URL

**Example:**
```bash
curl -X POST "https://api.telegram.org/bot123456789:ABC.../setWebhook" \
  -d "url=https://your-lambda-url.amazonaws.com/webhook/123456789:ABC..."
```

---

### 4. Get Webhook Info

**Purpose:** Check current webhook configuration

**URL Format:**
```
https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

**Example:**
```bash
curl "https://api.telegram.org/bot123456789:ABC.../getWebhookInfo"
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://your-webhook-url.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0,
    "max_connections": 40
  }
}
```

---

### 5. Delete Webhook

**Purpose:** Stop receiving updates via webhook (switch back to getUpdates polling)

**URL Format:**
```
https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook
```

**Example:**
```bash
curl -X POST "https://api.telegram.org/bot123456789:ABC.../deleteWebhook"
```

---

## ❌ Common Mistakes

### Mistake #1: Missing "bot" Prefix

**WRONG:**
```
https://api.telegram.org/123456789:ABC.../getUpdates
                          ❌ Missing "bot"
```

**CORRECT:**
```
https://api.telegram.org/bot123456789:ABC.../getUpdates
                          ✅
```

**Error you'll get:** `404 Not Found`

---

### Mistake #2: Space in Token

**WRONG:**
```
https://api.telegram.org/bot 123456789:ABC.../getUpdates
                             ❌ Space after "bot"
```

**CORRECT:**
```
https://api.telegram.org/bot123456789:ABC.../getUpdates
                             ✅ No space
```

---

### Mistake #3: Incorrect Token Format

**Valid token format:**
```
<numbers>:<alphanumeric_string>

Example: 123456789:ABCdefGHI-jklmnoPQRsTUVwxyz123
         ^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         Bot ID     Authentication token
```

If your token doesn't follow this format, it's not valid.

---

## 🧪 Testing Your Token

Quick test to verify your token works:

```bash
# Replace YOUR_TOKEN with your actual token
curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
```

**Success response:**
```json
{
  "ok": true,
  "result": {
    "id": 8085599904,
    "is_bot": true,
    "first_name": "My Expense Bot",
    "username": "my_expense_tracker_bot"
  }
}
```

**Error response (404):**
```html
<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
...
```
→ Check you included `bot` prefix!

---

## 📚 Full API Reference

For complete documentation of all available methods:

**Official Docs:** https://core.telegram.org/bots/api

**Key sections:**
- Getting Updates: https://core.telegram.org/bots/api#getting-updates
- Sending Messages: https://core.telegram.org/bots/api#sendmessage
- Webhooks: https://core.telegram.org/bots/api#setwebhook

---

## 🔐 Security Notes

1. **Never share your bot token publicly**
   - It's like a password
   - Anyone with it can control your bot

2. **Use environment variables**
   - Don't hardcode tokens in code
   - Use `.env` files (and add to `.gitignore`)

3. **Webhook security**
   - Use HTTPS (required by Telegram)
   - Optionally: Include token in webhook path for validation

---

## 💡 Pro Tips

### Tip #1: Use Bot Token in Webhook Path

Instead of:
```
https://your-lambda.amazonaws.com/webhook
```

Use:
```
https://your-lambda.amazonaws.com/webhook/<YOUR_BOT_TOKEN>
```

Then in your code, verify the token matches before processing.

### Tip #2: Test Locally First

Before setting up webhooks, test with `getUpdates`:

```bash
# 1. Send message to your bot via Telegram
# 2. Check for updates
curl "https://api.telegram.org/botYOUR_TOKEN/getUpdates"
# 3. You should see your message
```

### Tip #3: Clear Pending Updates

If switching from webhook to polling, clear pending updates:

```bash
curl "https://api.telegram.org/botYOUR_TOKEN/getUpdates?offset=-1"
```

---

## 🆘 Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 404 Not Found | Missing `bot` prefix | Add `bot` before token |
| 401 Unauthorized | Invalid token | Check token from @BotFather |
| 400 Bad Request | Wrong parameters | Check API docs for method |
| 409 Conflict | Webhook + polling conflict | Delete webhook or stop polling |
| 429 Too Many Requests | Rate limit exceeded | Wait and implement backoff |

---

**Last Updated:** November 2, 2025  
**Based on:** Telegram Bot API 7.0+


