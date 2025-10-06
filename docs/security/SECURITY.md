# 🔐 Security Policy & Best Practices

**Project:** SaaS Cafeterías  
**Last Updated:** 2025-10-03  
**Version:** 1.0  

---

## 📋 Table of Contents

1. [Reporting Security Vulnerabilities](#reporting-security-vulnerabilities)
2. [Secrets Management](#secrets-management)
3. [Authentication & Authorization](#authentication--authorization)
4. [Environment Configuration](#environment-configuration)
5. [Development Guidelines](#development-guidelines)
6. [Production Deployment](#production-deployment)
7. [Incident Response](#incident-response)
8. [Compliance & Auditing](#compliance--auditing)

---

## 🚨 Reporting Security Vulnerabilities

### How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security issues via:
- **Email:** security@yourdomain.com (encrypted with PGP if possible)
- **Private vulnerability disclosure** on GitHub (if available)

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested remediation (if any)

### Response Timeline

- **Initial Response:** Within 24 hours
- **Triage:** Within 72 hours
- **Fix Timeline:** Based on severity (Critical: 7 days, High: 14 days, Medium: 30 days)
- **Disclosure:** Coordinated with reporter after fix is deployed

---

## 🔑 Secrets Management

### Never Commit These Files

```bash
# NEVER commit to Git:
.env
.env.local
.env.production
.env.staging
*.env  # Unless it's .env.example
docker-compose.secrets.yml
secrets/
*.pem
*.p12
*.key
```

### Always Use `.example` Templates

✅ **CORRECT:**
```bash
.env.example           # Template with placeholders
.env.production.example
docker-compose.yml     # No secrets, uses ${VARIABLES}
```

❌ **INCORRECT:**
```bash
.env                   # Actual secrets
.env.production        # Production credentials
config.py              # Hardcoded API keys
```

### Generating Secure Secrets

#### JWT Secret Keys
```bash
# Generate 64-character secret
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### Database Passwords
```bash
# Generate 32-character password
openssl rand -base64 32
```

#### Backup Encryption Keys
```bash
# Generate base64-encoded 32-byte key
python -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

### Secrets Rotation Policy

| Secret Type | Rotation Frequency | Priority |
|-------------|-------------------|----------|
| JWT_SECRET | Every 90 days | CRITICAL |
| DATABASE_PASSWORD | Every 180 days | CRITICAL |
| API Keys (external) | Per vendor policy | HIGH |
| REDIS_PASSWORD | Every 180 days | MEDIUM |
| Webhook Secrets | Every 180 days | MEDIUM |

### Using Secrets Management Tools

#### Option 1: Environment Variables (Development)
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
```

#### Option 2: HashiCorp Vault (Production)
```python
from app.services_directory.secrets_service import secrets_manager

async def get_db_password():
    db_secret = await secrets_manager.get_secret("database")
    return db_secret["password"]
```

#### Option 3: AWS Secrets Manager
```bash
# Configure in .env
SECRETS_BACKEND=aws
AWS_REGION=us-east-1
```

---

## 🛡️ Authentication & Authorization

### Password Requirements

**Minimum Requirements:**
- Length: 8+ characters
- Complexity: Mix of uppercase, lowercase, numbers, special chars
- No common passwords (123456, password, etc.)

**Implementation:**
```python
# In app/core/security.py
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGITS = True
REQUIRE_SPECIAL_CHARS = True
```

### JWT Token Best Practices

**Token Configuration:**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30    # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS=7       # Longer for UX
ALGORITHM=HS256                    # Secure algorithm
```

**Token Storage:**
- ✅ **Backend:** Use httpOnly cookies or secure headers
- ✅ **Frontend:** Store in memory (Zustand/Redux) or sessionStorage
- ❌ **NEVER:** Store in localStorage for sensitive apps

**Token Validation:**
```python
# Always verify:
1. Signature validity
2. Expiration time (exp claim)
3. Issuer (iss claim)
4. Audience (aud claim)
5. Not before (nbf claim)
```

### Role-Based Access Control (RBAC)

**Defined Roles:**
- `admin`: Full system access
- `business_owner`: Manage own businesses
- `employee`: Limited access to assigned businesses
- `user`: Read-only access

**Permission Checks:**
```python
from app.api.v1.dependencies import get_current_admin_user

@router.post("/admin/users")
async def create_user(
    current_user: User = Depends(get_current_admin_user)
):
    # Only admin can access
    pass
```

---

## ⚙️ Environment Configuration

### Development Environment

```env
# .env (local development)
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./saas_cafeterias_local.db
SECRET_KEY=dev-only-not-for-production
```

**Security Notes:**
- SQLite is acceptable for local development
- Debug mode can be enabled
- Weak secrets are acceptable (but label them clearly)
- Use sandbox APIs (MercadoPago TEST mode, OpenAI dev keys)

### Staging Environment

```env
# .env.staging (testing environment)
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql://user:STRONG_PASSWORD@staging-db:5432/saas_staging
SECRET_KEY=UNIQUE_STAGING_SECRET_64_CHARS
```

**Security Notes:**
- Use production-like database (PostgreSQL)
- Disable debug mode
- Use unique secrets (different from production)
- Test with sandbox APIs when possible

### Production Environment

```env
# .env.production (NEVER commit this file!)
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://prod_user:COMPLEX_PASSWORD@prod-db:5432/saas_prod
SECRET_KEY=UNIQUE_PRODUCTION_SECRET_64_CHARS_ROTATED_QUARTERLY
```

**CRITICAL Requirements:**
- ✅ Strong, unique secrets (64+ characters)
- ✅ Encrypted database connections (SSL/TLS)
- ✅ Password-protected Redis
- ✅ Production API keys (MercadoPago PROD mode)
- ✅ HTTPS-only (no HTTP)
- ✅ Restrictive CORS (specific domains only)
- ❌ NO debug mode
- ❌ NO default passwords
- ❌ NO wildcards in ALLOWED_ORIGINS

---

## 👨‍💻 Development Guidelines

### Pre-Commit Checks

**Install git-secrets:**
```bash
# One-time setup
./setup_git_secrets.sh

# This installs:
# - pre-commit hooks
# - detect-secrets
# - git-secrets (if available)
# - Custom pattern matching
```

**What Gets Blocked:**
- Files matching `*.env.production`, `*.env.local`
- Strings matching secret patterns (passwords, API keys, tokens)
- Private keys (.pem, .key files)
- Database connection strings with credentials

**Bypass (Emergency Only):**
```bash
# Use with extreme caution!
git commit --no-verify -m "emergency fix"
```

### Code Review Checklist

**Security Review:**
- [ ] No hardcoded secrets or credentials
- [ ] No SQL injection vulnerabilities (use parameterized queries)
- [ ] No XSS vulnerabilities (sanitize user input)
- [ ] Proper authentication on all protected endpoints
- [ ] Role-based authorization correctly implemented
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't expose secrets

**API Security:**
- [ ] Rate limiting implemented
- [ ] Input validation (Pydantic schemas)
- [ ] CORS configured restrictively
- [ ] CSRF protection for state-changing operations
- [ ] SQL injection prevention (SQLAlchemy ORM)

### Testing Security

**Run Security Tests:**
```bash
# Full security test suite
python tests/test_business_flow_security.py

# Check for exposed secrets
./remediate_secrets.sh --dry-run

# Audit dependencies
pip-audit
npm audit
```

---

## 🚀 Production Deployment

### Pre-Deployment Checklist

**Environment:**
- [ ] All `.env` files use unique, strong secrets
- [ ] No `.env` files committed to repository
- [ ] Secrets rotated from any previous test/staging environments
- [ ] Database uses encrypted connections (SSL/TLS)
- [ ] Redis requires authentication

**Application:**
- [ ] `DEBUG=false` in all production configs
- [ ] `ENVIRONMENT=production` set
- [ ] CORS allows only specific production domains
- [ ] Rate limiting enabled and tested
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)

**Monitoring:**
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured (structured JSON logs)
- [ ] Audit logging enabled for sensitive operations
- [ ] Alerts set up for:
  - Multiple failed authentication attempts
  - Unusual API usage patterns
  - Server errors (5xx responses)
  - High latency endpoints

**Backups:**
- [ ] Automated daily database backups
- [ ] Backup encryption configured
- [ ] Backup restoration tested
- [ ] Off-site backup storage configured

### Post-Deployment Verification

```bash
# 1. Health check
curl https://api.yourdomain.com/health

# 2. Authentication flow
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'

# 3. Protected endpoint (should return 401 without token)
curl https://api.yourdomain.com/api/v1/users/me

# 4. Check security headers
curl -I https://api.yourdomain.com
# Should include: Strict-Transport-Security, X-Content-Type-Options, etc.
```

### Deployment Security

**CI/CD Pipeline:**
- Use secrets management in CI/CD (GitHub Secrets, GitLab CI/CD variables)
- Never log secrets in CI/CD output
- Scan for vulnerabilities before deployment
- Run security tests in pipeline

**Docker Security:**
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Use specific versions (not :latest)
FROM python:3.11-slim

# Scan images
RUN pip install safety && safety check
```

---

## 🚨 Incident Response

### Incident Severity Levels

| Severity | Definition | Response Time | Examples |
|----------|-----------|---------------|----------|
| CRITICAL | Data breach, service down | < 1 hour | Exposed credentials, database compromise |
| HIGH | Partial service impact | < 4 hours | Authentication bypass, API abuse |
| MEDIUM | Security flaw found | < 24 hours | Missing validation, weak encryption |
| LOW | Minor issue | < 7 days | Outdated dependency, verbose errors |

### Incident Response Procedure

**1. Discovery & Containment (0-1 hour)**
- Document the incident (what, when, how discovered)
- Isolate affected systems if needed
- Preserve evidence (logs, database state)
- Execute `remediate_secrets.sh` if credentials exposed

**2. Eradication (1-4 hours)**
- Rotate all potentially compromised secrets
- Patch vulnerabilities
- Remove unauthorized access
- Clean compromised data

**3. Recovery (4-24 hours)**
- Restore systems to normal operation
- Verify all services functional
- Monitor for recurrence
- Communicate with affected users (if applicable)

**4. Post-Incident (24-72 hours)**
- Complete incident report (`INCIDENT_REPORT.md`)
- Conduct post-mortem meeting
- Update security procedures
- Implement preventive measures

### Emergency Contacts

```yaml
Incident Commander: [Name/Email/Phone]
Security Lead: [Name/Email/Phone]
DevOps Lead: [Name/Email/Phone]
Database Admin: [Name/Email/Phone]
Legal/Compliance: [Name/Email/Phone]
```

---

## 📊 Compliance & Auditing

### Audit Logging

**What to Log:**
- User authentication (login/logout)
- Permission changes
- Data access (sensitive resources)
- Configuration changes
- Failed authentication attempts
- API rate limit violations

**What NOT to Log:**
- Passwords (even hashed)
- Full credit card numbers
- API keys or tokens
- Personal identification numbers (PINs)

**Log Format:**
```json
{
  "timestamp": "2025-10-03T14:30:00Z",
  "user_id": "user_123",
  "action": "user.login",
  "resource": "/api/v1/auth/login",
  "ip_address": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "status": "success"
}
```

### Compliance Standards

**GDPR (if handling EU data):**
- Right to access
- Right to deletion
- Data portability
- Consent management
- Breach notification (72 hours)

**PCI DSS (if handling payments):**
- Encryption of cardholder data
- Secure network
- Access control
- Monitoring and testing
- Information security policy

**SOC 2 (for enterprise customers):**
- Security
- Availability
- Processing integrity
- Confidentiality
- Privacy

### Security Audit Checklist

**Quarterly Review:**
- [ ] Review all user permissions
- [ ] Audit API keys and rotate if needed
- [ ] Check for unused accounts (disable/delete)
- [ ] Review access logs for anomalies
- [ ] Update dependencies (security patches)
- [ ] Test backup restoration
- [ ] Review and update this SECURITY.md

**Annual Review:**
- [ ] Full penetration testing
- [ ] Security training for team
- [ ] Third-party security audit
- [ ] Disaster recovery drill
- [ ] Update incident response procedures

---

## 📚 Additional Resources

### Internal Documentation
- [INCIDENT_REPORT.md](INCIDENT_REPORT.md) - Template for security incidents
- [ROTATION_CHECKLIST.md](ROTATION_CHECKLIST.md) - Secrets rotation guide
- [remediate_secrets.sh](remediate_secrets.sh) - Emergency remediation script

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)

### Security Tools
- **SAST:** Bandit (Python), ESLint (JavaScript)
- **Dependency Scanning:** pip-audit, npm audit, Snyk
- **Secrets Detection:** git-secrets, detect-secrets, TruffleHog
- **Container Scanning:** Trivy, Clair
- **Penetration Testing:** OWASP ZAP, Burp Suite

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-03 | Initial security policy created |

---

## ✅ Acknowledgment

By contributing to this project, you acknowledge that you have read and agree to follow this security policy.

**Questions?** Contact the security team at security@yourdomain.com

---

*"Security is not a product, but a process." - Bruce Schneier*
