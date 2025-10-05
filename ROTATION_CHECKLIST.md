# 🔐 SECRETS ROTATION CHECKLIST - EMERGENCY RESPONSE

**Date Created:** 2025-10-03  
**Incident:** Exposed credentials in repository (.env.production.secure)  
**Priority:** CRITICAL - Complete within 2 hours  
**Repository:** https://github.com/gonzacba17/Saas-inicial

---

## ⚠️ CRITICAL CONTEXT

**Exposed Files:**
- `.env.production.secure` (committed to Git history)
- `docker-compose.secrets.yml` (development tokens visible)

**Exposure Duration:** Unknown - assume compromised since first commit (c4e5034)  
**Public Exposure:** Yes - public repository  

---

## 🎯 ROTATION PRIORITY ORDER

### TIER 1 - IMMEDIATE (0-30 minutes)

#### ✅ 1. JWT SECRET KEY
- **Current Status:** ⚠️ Template value in .env.production.secure
- **Impact:** Session hijacking, authentication bypass
- **Action Required:**
  ```bash
  # Generate new 64-character secret
  python3 -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Update Locations:**
  - [ ] Production environment variables
  - [ ] `.env.production.secure` (local only - NOT in Git)
  - [ ] Kubernetes secrets / Docker secrets
  - [ ] Update backend/app/core/config.py if hardcoded
- **Validation:**
  ```bash
  # Verify new secret is active
  curl -X POST https://api.yourdomain.com/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"test"}'
  # Should return new token format
  ```
- **Side Effects:** All active user sessions will be invalidated
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 2. DATABASE PASSWORD (PostgreSQL)
- **Current Status:** ⚠️ Template value "CHANGE_TO_STRONG_DB_PASSWORD"
- **Impact:** Full database access, data exfiltration
- **Action Required:**
  ```bash
  # Generate 32-character password
  openssl rand -base64 32
  ```
- **Rotation Steps:**
  ```sql
  -- Connect as superuser
  psql -U postgres -h your-postgres-host.com
  
  -- Change password
  ALTER USER saasuser WITH PASSWORD 'new_secure_password_here';
  
  -- Verify
  \du saasuser
  ```
- **Update Locations:**
  - [ ] Production environment variables (POSTGRES_PASSWORD)
  - [ ] Database connection strings (DATABASE_URL)
  - [ ] Backend service configuration
  - [ ] Docker Compose production files
  - [ ] CI/CD pipeline secrets
- **Validation:**
  ```bash
  # Test connection with new password
  psql "postgresql://saasuser:NEW_PASSWORD@host:5432/saas_cafeterias_prod" -c "SELECT 1;"
  ```
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 3. REDIS PASSWORD
- **Current Status:** ⚠️ Template value "CHANGE_TO_REDIS_PASSWORD"
- **Impact:** Cache poisoning, session manipulation
- **Action Required:**
  ```bash
  # Generate Redis password
  openssl rand -base64 24
  ```
- **Rotation Steps:**
  ```bash
  # Update redis.conf
  redis-cli CONFIG SET requirepass "new_redis_password"
  redis-cli CONFIG REWRITE
  
  # Or restart Redis with new password
  ```
- **Update Locations:**
  - [ ] REDIS_PASSWORD environment variable
  - [ ] REDIS_URL (redis://:password@host:6379/0)
  - [ ] CELERY_BROKER_URL
  - [ ] CELERY_RESULT_BACKEND
  - [ ] Backend cache configuration
- **Validation:**
  ```bash
  redis-cli -h your-redis-host.com -a NEW_PASSWORD PING
  # Should return: PONG
  ```
- **Timeline:** ✓ Complete by: ___________

---

### TIER 2 - HIGH PRIORITY (30-60 minutes)

#### ✅ 4. MERCADOPAGO ACCESS TOKEN
- **Current Status:** ⚠️ Template "APP_USR_YOUR_PRODUCTION_ACCESS_TOKEN"
- **Impact:** Unauthorized payments, financial fraud
- **Action Required:**
  1. Login to MercadoPago Developer Dashboard
  2. Navigate to: Applications → Your App → Production Credentials
  3. Click "Regenerate Credentials"
  4. Copy new ACCESS_TOKEN and PUBLIC_KEY
- **Update Locations:**
  - [ ] MERCADOPAGO_ACCESS_TOKEN
  - [ ] MERCADOPAGO_PUBLIC_KEY
  - [ ] Frontend payment integration
  - [ ] Backend payment processing service
- **Validation:**
  ```bash
  curl -X GET "https://api.mercadopago.com/v1/payments/search" \
    -H "Authorization: Bearer YOUR_NEW_ACCESS_TOKEN"
  # Should return 200 OK
  ```
- **Additional Steps:**
  - [ ] Review recent transactions for suspicious activity
  - [ ] Enable MercadoPago webhook signature verification
  - [ ] Update MERCADOPAGO_WEBHOOK_SECRET
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 5. OPENAI API KEY
- **Current Status:** ⚠️ Template "sk-your-openai-api-key"
- **Impact:** Unauthorized API usage, cost implications
- **Action Required:**
  1. Login to OpenAI Platform: https://platform.openai.com
  2. Navigate to: API Keys
  3. Revoke existing key if present
  4. Generate new secret key
- **Update Locations:**
  - [ ] OPENAI_API_KEY environment variable
  - [ ] Backend AI service configuration
  - [ ] Any external integrations using OpenAI
- **Validation:**
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer NEW_API_KEY"
  # Should list available models
  ```
- **Cost Monitoring:**
  - [ ] Check usage dashboard for unauthorized calls
  - [ ] Set up usage limits/alerts
  - [ ] Review billing history
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 6. BACKUP ENCRYPTION KEY
- **Current Status:** ⚠️ Template "CHANGE_THIS_TO_BASE64_ENCODED_32_BYTE_KEY"
- **Impact:** Backup data exposure
- **Action Required:**
  ```bash
  # Generate new encryption key
  python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
  ```
- **Update Locations:**
  - [ ] BACKUP_ENCRYPTION_KEY environment variable
  - [ ] Backup service configuration
  - [ ] Document old key securely (for old backup decryption)
- **Important Notes:**
  - ⚠️ Old backups encrypted with old key cannot be decrypted with new key
  - Keep old key in secure vault for 90 days (backup retention period)
  - Re-encrypt critical backups with new key
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 7. WEBHOOK SECRETS
- **Current Status:** ⚠️ Template "CHANGE_THIS_TO_STRONG_WEBHOOK_SECRET_32_CHARS_MIN"
- **Impact:** Webhook spoofing, unauthorized callbacks
- **Action Required:**
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Update Locations:**
  - [ ] MERCADOPAGO_WEBHOOK_SECRET
  - [ ] Backend webhook validation logic
  - [ ] MercadoPago webhook configuration panel
- **Timeline:** ✓ Complete by: ___________

---

### TIER 3 - MEDIUM PRIORITY (60-120 minutes)

#### ✅ 8. DOCKER/VAULT DEVELOPMENT TOKENS
- **Exposure:** docker-compose.secrets.yml contains:
  - `VAULT_DEV_ROOT_TOKEN_ID=myroot`
  - `AWS_ACCESS_KEY_ID=test`
  - `AWS_SECRET_ACCESS_KEY=test`
- **Impact:** Local development environment compromise
- **Action Required:**
  - [ ] Regenerate Vault dev token
  - [ ] Update docker-compose.secrets.yml (keep OUT of Git)
  - [ ] Verify production Vault uses different credentials
- **Timeline:** ✓ Complete by: ___________

---

#### ✅ 9. SESSION SECRETS
- **Current Status:** Check for session management secrets
- **Action Required:**
  ```bash
  # If using Flask sessions or similar
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Update Locations:**
  - [ ] SESSION_SECRET / COOKIE_SECRET
  - [ ] Any stateful session storage
- **Timeline:** ✓ Complete by: ___________

---

## 🔍 VERIFICATION MATRIX

After rotation, verify each service:

| Service | Status | Test Command | Expected Result |
|---------|--------|--------------|-----------------|
| Backend API | ⬜ | `curl https://api.yourdomain.com/health` | 200 OK |
| Database | ⬜ | `psql DATABASE_URL -c "SELECT 1;"` | 1 row |
| Redis | ⬜ | `redis-cli -a PASSWORD PING` | PONG |
| Authentication | ⬜ | Login flow test | New JWT issued |
| Payments | ⬜ | Test MercadoPago transaction | Success |
| AI Features | ⬜ | Test OpenAI integration | Response received |
| Celery Workers | ⬜ | `celery -A app inspect ping` | pong |
| Webhooks | ⬜ | Trigger test webhook | Validated |

---

## 📋 POST-ROTATION ACTIONS

### Immediate (after rotation)
- [ ] Test complete user journey (signup → login → payment)
- [ ] Monitor error logs for authentication failures
- [ ] Check Sentry/monitoring for related errors
- [ ] Notify team of session invalidation

### Within 24 hours
- [ ] Update team password manager with new credentials
- [ ] Document incident in security log
- [ ] Schedule team security training
- [ ] Review access logs for suspicious activity

### Within 7 days
- [ ] Audit all environment files across all environments
- [ ] Implement git-secrets pre-commit hooks
- [ ] Set up secrets scanning in CI/CD
- [ ] Schedule quarterly secrets rotation policy

---

## 🚨 ROLLBACK PLAN

If services fail after rotation:

1. **Identify Failed Service**
   ```bash
   docker-compose logs backend | tail -50
   ```

2. **Restore Previous Secret (TEMPORARY)**
   - Use backup from `backup_pre_remediation_*/`
   - Update only the failing service
   - Document which secret was rolled back

3. **Investigate Root Cause**
   - Check for typos in new secrets
   - Verify all instances were updated
   - Check for cached old secrets

4. **Re-attempt Rotation**
   - Generate fresh secret
   - Update all locations simultaneously
   - Test thoroughly before marking complete

---

## 📞 ESCALATION CONTACTS

| Issue | Contact | Response Time |
|-------|---------|---------------|
| Database connectivity | DBA Team | < 15 min |
| Payment processing | Finance/DevOps | < 30 min |
| Production outage | On-call Engineer | Immediate |
| Security incident | Security Team | Immediate |

---

## ✅ COMPLETION SIGNATURE

**Rotation Completed By:** ___________________  
**Date/Time:** ___________________  
**All Tests Passed:** YES / NO  
**Incidents During Rotation:** ___________________  
**Next Rotation Due:** ___________________  

---

## 📚 REFERENCES

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- Project Documentation: `/docs/SECURITY.md`
- Incident Report: `INCIDENT_REPORT.md`

---

**REMEMBER:** 
- Document everything
- Test before deploying
- Coordinate with team
- Monitor post-deployment
- Secure old credentials for audit trail
