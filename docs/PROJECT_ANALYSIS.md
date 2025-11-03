# 🔍 Asistente de Gastos - Expert Analysis Report

**Date:** November 2, 2025  
**Analyst:** AI Assistant  
**Project Owner:** Santiago Aguirre

---

## 📋 Executive Summary

**Asistente de Gastos** is a **serverless AI-powered expense tracking application** that enables users to log personal expenses through Telegram, automatically categorize them using Google Gemini AI, and store them in Google Sheets.

### Quick Stats
- **Language:** Python 3.13
- **Architecture:** Serverless (AWS Lambda + Docker)
- **AI Model:** Google Gemini 2.0 Flash
- **Storage:** Google Sheets
- **Interface:** Telegram Bot
- **Infrastructure:** Terraform + Terragrunt
- **License:** MIT

---

## 🏗️ Architecture Deep Dive

### High-Level Flow
```
┌──────────┐      ┌─────────────┐      ┌────────────┐
│ Telegram │ ───> │ AWS Lambda  │ ───> │   Gemini   │
│   User   │      │   Docker    │      │     AI     │
└──────────┘      └─────────────┘      └────────────┘
                         │                      │
                         │                      ▼
                         │              ┌──────────────┐
                         │              │ JSON Extract │
                         │              │ - monto      │
                         │              │ - categoria  │
                         │              │ - descripción│
                         │              │ - fecha      │
                         │              └──────────────┘
                         │                      │
                         ▼                      ▼
                  ┌─────────────────────────────────┐
                  │     Google Sheets API           │
                  │  Append to "registros" sheet    │
                  └─────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  Telegram   │
                  │  Response   │
                  └─────────────┘
```

### Component Breakdown

#### 1. **Lambda Handler (`main.py`)**
**Responsibilities:**
- Receive Telegram webhook events
- Parse JSON body to extract message text and chat_id
- User identification based on chat_id (hardcoded mapping)
- Orchestrate AI parsing and Sheets storage
- Send confirmation back to Telegram

**Key Logic:**
```python
# User identification
if chat_id == 641045556:
    gasto["quien"] = "User1"
else:
    gasto["quien"] = "User2"
```

**Observations:**
- ✅ Good error handling with try/except
- ✅ Comprehensive logging
- ⚠️ Hardcoded user mapping (inflexible for scaling)
- ✅ Always returns 200 status (good for Telegram webhook)

#### 2. **AI Parser (`llm.py`)**
**Model:** Gemini 2.0 Flash  
**Configuration:**
- `response_mime_type: application/json` (enforces JSON output)
- System prompt with strict JSON schema

**Prompt Engineering:**
```
Eres un extractor de información. Devuelves SOLO JSON válido, sin texto adicional.
- NO inventes fechas
- Si usuario NO menciona fecha, devuelve null
- Categorías permitidas: servicios domesticos, gastos, comida, transporte, 
  mercado, ocio, salud, otros
```

**Observations:**
- ✅ Excellent prompt design (clear, structured)
- ✅ JSON schema enforcement via API parameter
- ✅ Smart date handling (null if not mentioned, then defaults to today)
- ✅ Predefined categories for consistency
- ⚠️ Timezone hardcoded to "America/Bogota"
- ⚠️ API key printed to logs (security concern)

#### 3. **Sheets Integration (`sheets.py`)**
**Authentication:** Service Account (base64 encoded)  
**Target Range:** `registros!A:D` (should be `A:E` for 5 columns)

**Data Structure:**
```python
[fecha, monto, categoria, descripcion, quien]
```

**Observations:**
- ✅ Clean service account credential handling
- ⚠️ Range mismatch: `A:D` is 4 columns, but we're writing 5 values
- ✅ USER_ENTERED value input option (allows formulas)
- ❌ No error handling for Google API failures
- ❌ No validation of credentials existence

#### 4. **Infrastructure (Terraform)**

**Lambda Configuration:**
- Timeout: 15 seconds
- Package Type: Image (Docker)
- Authorization: NONE (public Lambda URL)
- IAM Roles: Basic execution + ECR readonly

**Observations:**
- ✅ Proper IAM role separation
- ✅ ECR integration for Docker images
- ✅ Lambda Function URL enabled
- ⚠️ No CloudWatch alarms or monitoring
- ⚠️ No VPC configuration
- ⚠️ Timeout of 15s might be short for cold starts
- ⚠️ Typo in directory name: `lamda` should be `lambda`

---

## 🔐 Security Analysis

### Current Implementation

| Component | Status | Risk Level | Notes |
|-----------|--------|------------|-------|
| Lambda URL | Public | 🟡 Medium | No authentication - relies on Telegram token in URL path |
| API Keys in Logs | ❌ Exposed | 🔴 High | `print(os.environ["GEMINI_API_KEY"])` in llm.py |
| Credentials Storage | ✅ Base64 env | 🟢 Low | Properly handled via environment variables |
| User Authentication | ⚠️ Chat ID | 🟡 Medium | Hardcoded chat IDs - easy to spoof |
| Secrets in Code | ✅ None | 🟢 Low | All secrets via env vars |

### Recommendations
1. **URGENT:** Remove API key print statement from `llm.py:11`
2. Implement Telegram webhook token validation
3. Consider AWS Secrets Manager for credentials
4. Add IP allowlist or API Gateway with API key
5. Implement rate limiting

---

## 📊 Code Quality Assessment

### Strengths
1. ✅ **Clear separation of concerns** (handler, AI, storage)
2. ✅ **Comprehensive documentation** (README is excellent)
3. ✅ **Modern Python** (3.13, type hints would improve)
4. ✅ **Dependency locking** (uv.lock, requirements.txt)
5. ✅ **IaC with Terraform** (reproducible infrastructure)
6. ✅ **Logging** (good use of logger)

### Weaknesses
1. ❌ **No type hints** (would improve IDE support and catch errors)
2. ❌ **No tests** (unit, integration, or E2E)
3. ❌ **Hardcoded values** (user IDs, timezone, categories)
4. ❌ **No error recovery** (what if Sheets is down?)
5. ❌ **No input validation** (message length, chat_id format)
6. ❌ **Unused dependencies** (fastapi, uvicorn not used in Lambda)

---

## 🐛 Issues Found

### Critical
1. **Google Sheets Range Mismatch**
   - Range: `A:D` (4 columns)
   - Data: 5 columns (fecha, monto, categoria, descripcion, quien)
   - **Fix:** Change to `registros!A:E`

2. **API Key Exposure in Logs**
   - Line: `llm.py:11` - `print(os.environ["GEMINI_API_KEY"])`
   - **Fix:** Remove this line immediately

### High
3. **No Error Handling in Sheets Integration**
   - Google API calls can fail
   - **Fix:** Add try/except with proper error messages

4. **Hardcoded User Mapping**
   - Only supports 2 users with hardcoded chat IDs
   - **Fix:** Use environment variable or database lookup

### Medium
5. **Timezone Hardcoded**
   - `TZ = ZoneInfo("America/Bogota")`
   - **Fix:** Make configurable via environment variable

6. **Infrastructure Path Improvements**
   - ✅ Renamed to `infra/` for consistency
   - ✅ Fixed typo: `lamda/` → `lambda/`

7. **Unused Dependencies**
   - FastAPI and Uvicorn included but not used
   - **Fix:** Remove from pyproject.toml and requirements.txt

### Low
8. **No Type Hints**
   - Functions lack return type annotations
   - **Fix:** Add type hints throughout

9. **No Input Validation**
   - Message text not validated before parsing
   - **Fix:** Add length checks, sanitization

---

## 📈 Performance Analysis

### Current Metrics (Estimated)

| Metric | Value | Notes |
|--------|-------|-------|
| Cold Start | ~2-3s | Docker image + dependencies |
| Warm Execution | ~500-800ms | Gemini API is the bottleneck |
| Memory Usage | ~256MB | Could optimize to 128MB |
| Cost per 1000 requests | ~$0.02 | Very efficient |

### Optimization Opportunities
1. **Lambda Memory:** Currently unspecified, recommend 512MB for consistent performance
2. **Docker Image Size:** Could use multi-stage build to reduce size
3. **Dependency Pruning:** Remove unused packages (fastapi, uvicorn)
4. **Caching:** Could cache Gemini responses for duplicate messages

---

## 🚀 Feature Gaps & Enhancement Ideas

### Missing Features
1. **Data Validation**
   - No checks for valid amounts (negative numbers?)
   - No category validation
   - No duplicate detection

2. **Error Recovery**
   - No retry logic for API failures
   - No dead letter queue for failed messages

3. **Analytics**
   - No CloudWatch metrics
   - No custom dashboards
   - No alerting

4. **User Experience**
   - No help command
   - No edit/delete functionality
   - No expense history query
   - No receipt image upload

### Enhancement Ideas
1. **Multi-user Support**
   - Dynamic user registration
   - User settings (timezone, default categories)
   - Shared expense tracking

2. **Advanced Parsing**
   - Receipt OCR (using Amazon Textract)
   - Multiple expenses in one message
   - Recurring expenses

3. **Reporting**
   - Monthly summary via Telegram
   - Budget alerts
   - Category breakdown charts

4. **Integration**
   - Export to CSV/Excel
   - Sync with accounting software
   - Multi-language support

---

## 🧪 Testing Strategy (Currently Missing)

### Recommended Test Suite

```
tests/
├── unit/
│   ├── test_llm.py           # Mock Gemini responses
│   ├── test_sheets.py         # Mock Google API
│   └── test_main.py           # Handler logic
├── integration/
│   ├── test_telegram_flow.py  # End-to-end with test bot
│   └── test_sheets_write.py   # Real Google Sheets test
└── fixtures/
    ├── telegram_messages.json
    └── gemini_responses.json
```

### Test Coverage Goals
- Unit Tests: 80%+
- Integration Tests: Key flows
- E2E Tests: At least 1 happy path

---

## 📦 Deployment Analysis

### Current Process
```bash
# 1. Build
docker buildx build --platform linux/amd64 -t asistente-gastos:vX .

# 2. Tag
docker tag asistente-gastos:vX <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/asistente-gastos:vX

# 3. Push
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/asistente-gastos:vX

# 4. Update Lambda
aws lambda update-function-code --function-name asistente-gastos --image-uri <URI>
```

### Observations
- ✅ Manual process documented
- ❌ No CI/CD automation
- ❌ No automated testing before deploy
- ❌ No rollback strategy
- ❌ No staging environment

### Recommendations
1. **GitHub Actions CI/CD Pipeline**
   - Automated testing on PR
   - Automated build on merge to main
   - Automated deploy to staging → production

2. **Versioning Strategy**
   - Semantic versioning for releases
   - Git tags for releases
   - Automated changelog

---

## 🔧 Dependency Analysis

### Core Dependencies
| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| google-generativeai | 0.8.5 | Gemini AI | ✅ Current |
| google-api-python-client | 2.185.0 | Sheets API | ✅ Current |
| google-auth | 2.41.1 | Authentication | ✅ Current |
| requests | 2.32.5 | Telegram API | ✅ Current |
| python-dotenv | 1.1.1 | Env vars | ✅ Current |

### Unnecessary Dependencies
| Package | Reason | Action |
|---------|--------|--------|
| fastapi | Not used in Lambda | ❌ Remove |
| uvicorn | Not used in Lambda | ❌ Remove |

### Security Considerations
- All dependencies are reasonably up-to-date
- No known critical vulnerabilities
- Recommend: `pip-audit` or `safety` for ongoing monitoring

---

## 💰 Cost Analysis

### AWS Costs (Estimated Monthly)

**Assumptions:**
- 1000 expenses/month (~33/day)
- 128MB Lambda, 800ms avg duration
- 1GB ECR storage

| Service | Cost | Notes |
|---------|------|-------|
| Lambda | $0.01 | 1000 requests × 800ms × 128MB |
| ECR | $0.10 | ~1GB image storage |
| Data Transfer | $0.01 | Minimal egress |
| **Total** | **~$0.12/month** | Extremely cost-effective |

### External API Costs

| Service | Cost | Notes |
|---------|------|-------|
| Gemini API | $0.00 | Free tier: 1500 req/day |
| Google Sheets | $0.00 | Free |
| Telegram | $0.00 | Free |
| **Total** | **$0.00** | All within free tiers |

**Total Monthly Cost: ~$0.12** ✅

---

## 📝 Configuration Management

### Environment Variables Required

```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...

# Google AI
GEMINI_API_KEY=AIzaSy...

# Google Sheets
GOOGLE_SHEET_ID=1a2b3c4d5e6f...
GOOGLE_CREDENTIALS_JSON_BASE64=eyJ0eXBlIjoi...

# Optional (currently hardcoded)
TIMEZONE=America/Bogota
USER1_CHAT_ID=641045556
USER2_NAME=User2
```

### Missing Configuration
- ❌ No .env.example file
- ❌ No config validation on startup
- ❌ No fallback values for optional configs

---

## 🎯 Recommendations Summary

### Immediate (Fix Now)
1. ❌ **Remove API key print** in `llm.py:11`
2. ❌ **Fix Sheets range** from `A:D` to `A:E`
3. ❌ **Add error handling** to sheets.py
4. ❌ **Remove unused dependencies** (fastapi, uvicorn)

### Short-term (This Week)
5. ⚠️ **Add type hints** throughout codebase
6. ⚠️ **Create .env.example** file
7. ⚠️ **Add type hints** throughout codebase
8. ⚠️ **Add input validation** to Lambda handler
9. ⚠️ **Implement basic tests** (at least unit tests)

### Medium-term (This Month)
10. 🔵 **Setup CI/CD pipeline** (GitHub Actions)
11. 🔵 **Add CloudWatch alarms** (errors, duration)
12. 🔵 **Externalize user configuration** (remove hardcoded IDs)
13. 🔵 **Add help command** to bot
14. 🔵 **Implement retry logic** for external APIs

### Long-term (Future Enhancements)
15. 🟢 **Receipt OCR** support
16. 🟢 **Monthly reports** automation
17. 🟢 **Multi-user** dynamic registration
18. 🟢 **Budget alerts** feature
19. 🟢 **Web dashboard** for analytics

---

## 📚 Documentation Quality

### Current State
- ✅ **README.md** is excellent (9/10)
  - Clear architecture diagram
  - Comprehensive setup instructions
  - Deployment guide
  - Troubleshooting section
  - Webhook integration guide

### Missing Documentation
- ❌ No inline code comments
- ❌ No API documentation
- ❌ No troubleshooting guide
- ❌ No contribution guidelines
- ❌ No changelog

### Recommended Additions
1. `CONTRIBUTING.md` - How to contribute
2. `CHANGELOG.md` - Version history
3. `docs/TROUBLESHOOTING.md` - Common issues
4. `docs/DEVELOPMENT.md` - Local dev setup
5. Inline docstrings for all functions

---

## 🎓 Code Maturity Level

**Current Assessment: 6/10** (Functional, Needs Improvement)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Functionality | 9/10 | Works as intended |
| Code Quality | 5/10 | No types, no tests |
| Security | 6/10 | API key exposure issue |
| Performance | 8/10 | Efficient serverless |
| Scalability | 4/10 | Hardcoded user limits |
| Maintainability | 6/10 | Good structure, needs tests |
| Documentation | 8/10 | README excellent, code needs comments |
| DevOps | 5/10 | Manual deployment, no CI/CD |

---

## ✅ Conclusion

**Asistente de Gastos** is a **well-architected proof-of-concept** that successfully demonstrates serverless AI integration for personal expense tracking. The project shows strong fundamentals in:

- Clean code organization
- Modern tech stack
- Infrastructure as Code
- Excellent documentation

However, it requires several improvements before being production-ready:

### Critical Path to Production:
1. Fix security issues (API key exposure)
2. Add comprehensive error handling
3. Implement testing suite
4. Setup CI/CD pipeline
5. Add monitoring and alerting
6. Externalize configuration
7. Add user management

### Overall Rating: **B+ (Good, with clear path to Excellent)**

The project is a solid foundation that with focused improvements could become a robust, scalable expense tracking solution.

---

**Next Steps:** Would you like me to create a detailed implementation plan for any of these recommendations?


