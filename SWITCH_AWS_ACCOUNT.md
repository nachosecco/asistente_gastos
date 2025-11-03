# 🔄 Switch AWS Account - Quick Guide

**Old Account:** 555199228203  
**New Account:** 344666582324

---

## Option 1: Reconfigure Default Profile (Recommended)

### Step 1: Get Access Keys for New Account

1. Log into AWS Console with account **344666582324**
2. Go to **IAM** → **Users**
3. Select your user or create new user: `asistente-gastos-deployer`
4. Go to **Security credentials** tab
5. Click **Create access key**
6. Select **CLI** use case
7. **COPY:**
   - Access Key ID (starts with `AKIA...`)
   - Secret Access Key (long string)

### Step 2: Configure AWS CLI

```bash
aws configure
```

**Enter when prompted:**
```
AWS Access Key ID: [paste new Access Key ID]
AWS Secret Access Key: [paste new Secret Access Key]
Default region name: us-east-1
Default output format: json
```

### Step 3: Verify New Account

```bash
aws sts get-caller-identity
```

Should show: `"Account": "344666582324"` ✅

---

## Option 2: Use Named Profile

Keep old account and add new one as a profile:

```bash
# Configure new profile
aws configure --profile new-account

# Then use it with --profile flag
aws sts get-caller-identity --profile new-account

# Or set as default for session
export AWS_PROFILE=new-account
```

---

## Option 3: Use Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-new-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-new-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Verify
aws sts get-caller-identity
```

---

## ⚠️ Important: IAM Permissions Needed

Your user in the new account needs these policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AWSLambda_FullAccess`
- `IAMFullAccess` (or at least create roles)

---

## After Switching Accounts

Once configured, run this to continue deployment:

```bash
export AWS_ACCOUNT_ID=344666582324
export AWS_REGION=us-east-1

# Verify you're using the right account
aws sts get-caller-identity
```

Then I'll help you complete the deployment! 🚀


