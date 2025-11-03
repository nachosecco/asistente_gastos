# 🚀 AWS Lambda Deployment Guide

**Goal:** Deploy your expense tracker to AWS Lambda so you can use it from Telegram!

**Time Required:** 20-30 minutes  
**Cost:** ~$0.12/month (or FREE if under 1M requests/month)

---

## 📋 What We'll Do

1. ✅ Create/verify AWS account
2. ✅ Set up AWS CLI
3. ✅ Create ECR repository
4. ✅ Build & push Docker image to ECR
5. ✅ Create Lambda function
6. ✅ Configure environment variables
7. ✅ Set up Telegram webhook
8. ✅ Test end-to-end!

---

## STEP 1: Verify AWS Account

**Do you have an AWS account?**

- **YES** → Skip to Step 2
- **NO** → Follow these steps:

### Create AWS Account

1. Go to: https://aws.amazon.com
2. Click **"Create an AWS Account"**
3. Follow the signup:
   - Email address
   - Password
   - Account name (your name is fine)
   - Contact info
   - **Credit card required** (won't be charged for free tier)
   - Phone verification
   - Choose "Basic Support - Free"

4. Sign in to AWS Console: https://console.aws.amazon.com

---

## STEP 2: Set AWS Region

1. Look at top-right corner (next to your account name)
2. Click the region dropdown
3. Select: **"us-east-1" (N. Virginia)** or **"sa-east-1" (São Paulo)**
   - us-east-1 = Most services, cheapest
   - sa-east-1 = Closer to you (Uruguay)

**We'll use:** `us-east-1` (recommended for Lambda)

---

## STEP 3: Install & Configure AWS CLI

### Install AWS CLI (macOS)

```bash
# Check if already installed
aws --version

# If not installed:
brew install awscli

# Verify installation
aws --version
```

### Configure AWS CLI

You need to create **Access Keys** first:

#### Create Access Keys

1. Go to AWS Console: https://console.aws.amazon.com
2. Search for "IAM" in the top search bar
3. Click **"Users"** in left sidebar
4. Click **"Create user"**
5. User name: `asistente-gastos-deployer`
6. Click **"Next"**
7. **Attach policies directly** → Search and select:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AWSLambda_FullAccess`
8. Click **"Next"** → **"Create user"**
9. Click on the newly created user
10. Go to **"Security credentials"** tab
11. Scroll to **"Access keys"** section
12. Click **"Create access key"**
13. Select **"Command Line Interface (CLI)"**
14. Check the confirmation box
15. Click **"Next"** → **"Create access key"**
16. **COPY BOTH:**
    - Access key ID (starts with `AKIA...`)
    - Secret access key (long string - you can only see it once!)

#### Configure CLI

```bash
aws configure
```

**Enter when prompted:**
```
AWS Access Key ID: [paste your Access Key ID]
AWS Secret Access Key: [paste your Secret Access Key]
Default region name: us-east-1
Default output format: json
```

**Test it works:**
```bash
aws sts get-caller-identity
```

You should see your account info! ✅

---

## STEP 4: Create ECR Repository

ECR (Elastic Container Registry) stores your Docker image.

```bash
# Create repository
aws ecr create-repository \
  --repository-name asistente-gastos \
  --region us-east-1

# Save the repository URI (you'll need it later)
# It looks like: 123456789012.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos
```

**Copy the `repositoryUri` from the output!**

---

## STEP 5: Build & Push Docker Image to ECR

### Get your AWS Account ID

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID: $AWS_ACCOUNT_ID"
```

### Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

Should see: **"Login Succeeded"** ✅

### Build Image for AWS Lambda

```bash
cd /Users/isecco/Code/Asistente_gastos

# Build for linux/amd64 (Lambda requirement)
docker buildx build --platform linux/amd64 \
  -t asistente-gastos:latest .
```

### Tag Image for ECR

```bash
docker tag asistente-gastos:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest
```

### Push to ECR

```bash
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest
```

This will take a few minutes... ⏳

---

## STEP 6: Create Lambda Function

### Create execution role for Lambda

```bash
# Create trust policy
cat > /tmp/lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
  --role-name asistente-gastos-lambda-role \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name asistente-gastos-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Wait 10 seconds for role to propagate
sleep 10
```

### Create Lambda function

```bash
# Get your account ID if not already set
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create Lambda function
aws lambda create-function \
  --function-name asistente-gastos \
  --package-type Image \
  --code ImageUri=$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest \
  --role arn:aws:iam::$AWS_ACCOUNT_ID:role/asistente-gastos-lambda-role \
  --timeout 30 \
  --memory-size 512 \
  --region us-east-1
```

---

## STEP 7: Configure Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name asistente-gastos \
  --environment "Variables={
    TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>,
    GEMINI_API_KEY=<GEMINI_API_KEY>,
    GOOGLE_SHEET_ID=<GOOGLE_SHEET_ID>,
    GOOGLE_CREDENTIALS_JSON_BASE64=<GOOGLE_CREDENTIALS_JSON_BASE64>
  }" \
  --region us-east-1
```

---

## STEP 8: Create Lambda Function URL

This creates a public HTTPS endpoint for your Lambda:

```bash
aws lambda create-function-url-config \
  --function-name asistente-gastos \
  --auth-type NONE \
  --region us-east-1
```

**Copy the `FunctionUrl` from the output!**  
It looks like: `https://abc123xyz.lambda-url.us-east-1.on.aws/`

### Add permissions for public access

```bash
aws lambda add-permission \
  --function-name asistente-gastos \
  --statement-id FunctionURLAllowPublicAccess \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type NONE \
  --region us-east-1
```

---

## STEP 9: Test Lambda Function

```bash
# Get your Lambda URL
export LAMBDA_URL=$(aws lambda get-function-url-config \
  --function-name asistente-gastos \
  --region us-east-1 \
  --query FunctionUrl \
  --output text)

echo "Your Lambda URL: $LAMBDA_URL"

# Test it
curl -X POST "$LAMBDA_URL" \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"gasté 30000 en cena","chat":{"id":807197442}}}'
```

**Expected response:** `ok` or similar success message

**Check your Google Sheet** - you should see the new expense!

---

## STEP 10: Configure Telegram Webhook

Now connect your Telegram bot to the Lambda:

```bash
# Set the webhook
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=$LAMBDA_URL"
```

**Expected response:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### Verify webhook is set

```bash
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

Should show your Lambda URL! ✅

---

## STEP 11: Test End-to-End! 🎉

**Open Telegram and send a message to your bot:**

```
@gastos_secco_grignola_bot
```

Send any of these:
- "Gasté 15000 en taxi"
- "Pagué 45000 en mercado"
- "Comí pizza por 20000"

**What should happen:**
1. ✅ Bot receives your message
2. ✅ Lambda processes it with Gemini AI
3. ✅ Expense is saved to Google Sheets
4. ✅ Bot sends confirmation back to you!

**Check your Google Sheet** to see all expenses! 📊

---

## 🔧 Useful Commands

### Update Lambda code (after changes)

```bash
# Rebuild and push image
cd /Users/isecco/Code/Asistente_gastos
docker buildx build --platform linux/amd64 -t asistente-gastos:latest .
docker tag asistente-gastos:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest

# Update Lambda to use new image
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos:latest \
  --region us-east-1
```

### View Lambda logs

```bash
aws logs tail /aws/lambda/asistente-gastos --follow --region us-east-1
```

### Update environment variables

```bash
aws lambda update-function-configuration \
  --function-name asistente-gastos \
  --environment "Variables={VAR_NAME=value,...}" \
  --region us-east-1
```

### Delete webhook (switch back to local testing)

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook"
```

---

## 🆘 Troubleshooting

### Lambda returns error

```bash
# Check logs
aws logs tail /aws/lambda/asistente-gastos --follow --region us-east-1

# Test Lambda directly
aws lambda invoke \
  --function-name asistente-gastos \
  --payload '{"message":{"text":"test","chat":{"id":807197442}}}' \
  --region us-east-1 \
  response.json

cat response.json
```

### Webhook not working

```bash
# Check webhook status
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"

# Reset webhook
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook"
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
  -d "url=YOUR_LAMBDA_URL"
```

### Image too large

If ECR push fails due to size:
- Remove unused dependencies from requirements.txt
- Use multi-stage Docker build

---

## 💰 Cost Estimate

**Lambda:**
- Free tier: 1M requests/month + 400,000 GB-seconds compute
- After free tier: ~$0.20 per 1M requests

**ECR:**
- Free tier: 500MB storage/month
- After: $0.10/GB/month

**Estimated total: $0.00 - $0.12/month** for typical usage! 🎉

---

## ✅ Deployment Checklist

- [ ] AWS account created
- [ ] AWS CLI configured
- [ ] ECR repository created
- [ ] Docker image pushed to ECR
- [ ] Lambda function created
- [ ] Environment variables configured
- [ ] Lambda URL created
- [ ] Telegram webhook configured
- [ ] End-to-end test successful
- [ ] Expense appears in Google Sheet
- [ ] Bot sends confirmation to Telegram

---

**Deployment Time:** ~30 minutes  
**Result:** Fully automated AI expense tracker! 🚀


