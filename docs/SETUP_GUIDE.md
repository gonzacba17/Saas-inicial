# 🚀 Secure Setup Guide - SaaS Cafeterías

**Purpose:** Step-by-step guide for secure environment configuration  
**Audience:** Developers, DevOps, System Administrators  
**Last Updated:** 2025-10-03

---

## 📋 Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Development Environment](#development-environment)
3. [Staging Environment](#staging-environment)
4. [Production Environment](#production-environment)
5. [Security Tools Installation](#security-tools-installation)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 First-Time Setup

### Prerequisites

Before starting, ensure you have:
- **Python 3.11+** installed ([Download](https://www.python.org/))
- **Node.js 20+** installed ([Download](https://nodejs.org/))
- **Git** installed and configured
- **PostgreSQL 15+** (for production/staging) or SQLite (for development)
- **Redis** (optional, for caching)

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/Saas-inicial.git
cd Saas-inicial

# Verify you're on the main branch
git branch
```

### Install Security Hooks (CRITICAL)

**Before making any changes, install git-secrets and pre-commit hooks:**

```bash
# This prevents committing secrets accidentally
./setup_git_secrets.sh

# Verify installation
pre-commit --version
git secrets --version  # May not be available on all systems
```

**What this does:**
- ✅ Blocks commits containing secrets
- ✅ Prevents production .env files from being committed
- ✅ Detects private keys and API tokens
- ✅ Runs code formatting checks (black, flake8)

---

## 💻 Development Environment

### Step 1: Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

### Step 2: Configure Development Variables

**Minimal configuration for local development:**

```env
# .env (for local development)

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (SQLite is fine for development)
DATABASE_URL=sqlite:///./saas_cafeterias_local.db

# Security (DEVELOPMENT ONLY - weak secrets are OK here)
SECRET_KEY=dev-secret-key-for-local-testing-only-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-for-testing
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (allow local frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: External APIs (use test/sandbox modes)
# REDIS_URL=redis://localhost:6379/0
# MERCADOPAGO_ACCESS_TOKEN=TEST-your-sandbox-token
# OPENAI_API_KEY=sk-proj-your-dev-key
```

**Important Notes:**
- 🔵 These are development-only values
- 🔵 Weak secrets are acceptable for local testing
- 🔵 SQLite is sufficient for local development
- 🔵 External APIs are optional (features will be limited without them)

### Step 3: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create initial admin user
python create_admin.py

# Start the backend server
python -m uvicorn app.main:app --reload
```

**Verify backend is running:**
```bash
# In a new terminal
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Check API documentation
open http://localhost:8000/docs  # or visit in browser
```

### Step 4: Setup Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create frontend environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the development server
npm run dev
```

**Verify frontend is running:**
- Open browser to http://localhost:5173
- You should see the login page
- Try logging in with: `admin@saas.test` / `Admin1234!`

### Step 5: Run Tests

```bash
# From project root
python tests/full_test.py

# Should see all tests passing
```

---

## 🧪 Staging Environment

### Step 1: Prepare Staging Server

**Server requirements:**
- Ubuntu 20.04+ or similar Linux distribution
- 2+ CPU cores, 4GB+ RAM
- PostgreSQL 15+ installed and configured
- Redis installed (optional but recommended)
- SSL certificate configured (Let's Encrypt recommended)

### Step 2: Create Staging Environment File

```bash
# On staging server, create .env.staging
cd /path/to/application
nano .env.staging
```

**Staging configuration:**

```env
# .env.staging

# Environment
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Database (PostgreSQL required)
POSTGRES_USER=staging_user
POSTGRES_PASSWORD=CHANGE_ME_generate_strong_password
POSTGRES_HOST=staging-db-host.internal
POSTGRES_PORT=5432
POSTGRES_DB=saas_cafeterias_staging

# Alternative: Use DATABASE_URL
DATABASE_URL=postgresql://staging_user:STRONG_PASSWORD@staging-db-host:5432/saas_cafeterias_staging

# Security (UNIQUE secrets for staging)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=STAGING_UNIQUE_SECRET_64_CHARS_DIFFERENT_FROM_PROD
JWT_SECRET_KEY=STAGING_JWT_SECRET_64_CHARS_UNIQUE
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (with password)
REDIS_HOST=staging-redis-host.internal
REDIS_PORT=6379
REDIS_PASSWORD=CHANGE_ME_redis_password
REDIS_URL=redis://:REDIS_PASSWORD@staging-redis-host:6379/0

# CORS (staging domain only)
ALLOWED_ORIGINS=https://staging.yourdomain.com

# External APIs (use sandbox/test modes)
MERCADOPAGO_ACCESS_TOKEN=TEST-your-staging-sandbox-token
MERCADOPAGO_PUBLIC_KEY=TEST-your-staging-public-key
OPENAI_API_KEY=sk-proj-your-staging-key

# Monitoring
SENTRY_DSN=https://your-staging-sentry-dsn@sentry.io/project
```

**Generate secrets:**
```bash
# On staging server
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_urlsafe(64))"
openssl rand -base64 32  # For database password
```

### Step 3: Deploy to Staging

```bash
# Build and deploy (example using Docker)
docker-compose -f docker-compose.staging.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python create_admin.py

# Check logs
docker-compose logs -f backend
```

### Step 4: Verify Staging Deployment

```bash
# Health check
curl https://staging-api.yourdomain.com/health

# Test authentication
curl -X POST https://staging-api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@saas.test","password":"Admin1234!"}'
```

---

## 🚀 Production Environment

### ⚠️ CRITICAL PRE-DEPLOYMENT CHECKLIST

**STOP! Before deploying to production, verify ALL of these:**

- [ ] All secrets are unique (different from staging/dev)
- [ ] Secrets are at least 64 characters long
- [ ] Database password is strong (24+ characters)
- [ ] Redis requires password authentication
- [ ] `DEBUG=false` in all configs
- [ ] CORS allows only production domains (no wildcards)
- [ ] SSL/TLS certificates are valid and installed
- [ ] Backups are configured and tested
- [ ] Monitoring/alerting is configured
- [ ] Rate limiting is enabled
- [ ] Security headers are configured
- [ ] No `.env` files in Git repository

### Step 1: Generate Production Secrets

**On your local machine (NOT on production server):**

```bash
# Generate all production secrets
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)"
echo "REDIS_PASSWORD=$(openssl rand -base64 24)"
echo "BACKUP_ENCRYPTION_KEY=$(python -c 'import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())')"
```

**Store these securely:**
- Use a password manager (1Password, LastPass, Bitwarden)
- Or use a secrets management service (HashiCorp Vault, AWS Secrets Manager)
- NEVER email or share in plain text
- NEVER commit to Git

### Step 2: Configure Production Environment

**On production server, create .env.production:**

```env
# .env.production (NEVER commit this file!)

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database (PostgreSQL with SSL)
POSTGRES_USER=prod_db_user
POSTGRES_PASSWORD=PASTE_GENERATED_PASSWORD_HERE
POSTGRES_HOST=prod-db-host.internal
POSTGRES_PORT=5432
POSTGRES_DB=saas_cafeterias_prod
POSTGRES_SSL_MODE=require

DATABASE_URL=postgresql://prod_db_user:PASSWORD@prod-db-host:5432/saas_cafeterias_prod?sslmode=require

# Security (UNIQUE production secrets)
SECRET_KEY=PASTE_GENERATED_SECRET_KEY_HERE
JWT_SECRET_KEY=PASTE_GENERATED_JWT_SECRET_HERE
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (MUST have password in production)
REDIS_HOST=prod-redis-host.internal
REDIS_PORT=6379
REDIS_PASSWORD=PASTE_GENERATED_REDIS_PASSWORD_HERE
REDIS_URL=redis://:REDIS_PASSWORD@prod-redis-host:6379/0

# Celery
CELERY_BROKER_URL=redis://:REDIS_PASSWORD@prod-redis-host:6379/1
CELERY_RESULT_BACKEND=redis://:REDIS_PASSWORD@prod-redis-host:6379/2

# CORS (ONLY production domains - NO wildcards)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# External APIs (PRODUCTION credentials)
MERCADOPAGO_ACCESS_TOKEN=APP_USR_PRODUCTION_TOKEN_FROM_DASHBOARD
MERCADOPAGO_PUBLIC_KEY=APP_USR_PRODUCTION_PUBLIC_KEY
MERCADOPAGO_WEBHOOK_SECRET=PASTE_GENERATED_WEBHOOK_SECRET_HERE

OPENAI_API_KEY=sk-proj-PRODUCTION_KEY_FROM_OPENAI

# Backup Encryption
BACKUP_ENCRYPTION_KEY=PASTE_GENERATED_ENCRYPTION_KEY_HERE

# Monitoring
SENTRY_DSN=https://your-production-sentry-dsn@sentry.io/project

# Email (if configured)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
EMAIL_FROM=noreply@yourdomain.com
```

### Step 3: Secure the Environment File

```bash
# Set restrictive permissions (owner read-only)
chmod 400 .env.production

# Verify permissions
ls -la .env.production
# Should show: -r-------- (400)

# Verify ownership
sudo chown app_user:app_user .env.production
```

### Step 4: Deploy to Production

```bash
# Pull latest code
git pull origin main

# Backup database before deployment
pg_dump -h prod-db-host -U prod_db_user saas_cafeterias_prod > backup_$(date +%Y%m%d).sql

# Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose restart

# Check logs for errors
docker-compose logs -f backend
```

### Step 5: Post-Deployment Verification

```bash
# 1. Health check
curl https://api.yourdomain.com/health

# 2. Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourdomain.com","password":"YourSecurePassword"}'

# 3. Verify HTTPS redirect
curl -I http://api.yourdomain.com
# Should return: 301 Moved Permanently (redirect to https)

# 4. Check security headers
curl -I https://api.yourdomain.com
# Should include:
# - Strict-Transport-Security
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY

# 5. Test a protected endpoint (should return 401)
curl https://api.yourdomain.com/api/v1/users/me
# Should return: {"detail":"Not authenticated"}

# 6. Monitor error logs
tail -f /var/log/saas-cafeterias/error.log
```

### Step 6: Configure Monitoring & Alerts

**Set up alerts for:**
- Server down (ping fails)
- High error rate (5xx responses)
- Failed authentication attempts (> 5 in 10 min)
- Database connection failures
- High memory/CPU usage

**Monitoring tools:**
- Prometheus + Grafana (configured in `monitoring/`)
- Sentry for error tracking
- Uptime monitoring (UptimeRobot, Pingdom)

---

## 🛠️ Security Tools Installation

### Git-Secrets & Pre-Commit Hooks

```bash
# Automated installation (recommended)
./setup_git_secrets.sh

# Manual installation
pip install pre-commit detect-secrets
pre-commit install
detect-secrets scan --baseline .secrets.baseline
```

### Dependency Scanning

```bash
# Python dependencies
pip install pip-audit
pip-audit

# Node.js dependencies
npm audit
npm audit fix

# Or use Snyk
npm install -g snyk
snyk test
```

### Container Scanning

```bash
# Install Trivy
brew install trivy  # Mac
# or
sudo apt-get install trivy  # Ubuntu

# Scan Docker images
trivy image saas-cafeterias-backend:latest
```

---

## 🔧 Troubleshooting

### Issue: "Permission denied" when accessing .env file

**Solution:**
```bash
# Check file ownership
ls -la .env

# Fix ownership
sudo chown $USER:$USER .env

# Fix permissions
chmod 600 .env
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Verify database is running
pg_isready -h localhost -p 5432

# Test connection with psql
psql -h localhost -U your_user -d saas_cafeterias

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database
```

### Issue: "JWT token validation failed"

**Solution:**
```bash
# Verify SECRET_KEY is set and correct
python -c "from app.core.config import settings; print(settings.secret_key)"

# Regenerate admin user
cd backend
python create_admin.py

# Clear browser cache and cookies
# Try logging in again
```

### Issue: "CORS error in browser"

**Solution:**
```bash
# Check ALLOWED_ORIGINS in .env
grep ALLOWED_ORIGINS .env

# Ensure it includes your frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Restart backend
docker-compose restart backend
```

### Issue: "Pre-commit hooks blocking commit"

**Solution:**
```bash
# Review what was blocked
git status

# Check for actual secrets
grep -r "SECRET_KEY" .

# If false positive, update .secrets.baseline
detect-secrets scan --baseline .secrets.baseline

# If emergency, bypass (use carefully!)
git commit --no-verify -m "message"
```

### Issue: "Redis connection refused"

**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis
sudo systemctl start redis  # Linux
brew services start redis  # Mac

# Test with password (if configured)
redis-cli -a your_redis_password PING
```

---

## 📚 Additional Resources

- **Main Documentation:** [docs/README.md](docs/README.md)
- **Security Policy:** [SECURITY.md](SECURITY.md)
- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Deployment Guide:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## ✅ Setup Verification Checklist

**After completing setup, verify:**

- [ ] Backend is accessible at http://localhost:8000/health
- [ ] Frontend is accessible at http://localhost:5173
- [ ] Can login with default admin credentials
- [ ] API documentation loads at http://localhost:8000/docs
- [ ] Git-secrets hooks are installed (`pre-commit run --all-files`)
- [ ] Tests pass (`python tests/full_test.py`)
- [ ] No secrets in Git history (`git log --all -S "SECRET_KEY"` shows only examples)

---

**Need help?** Check [SECURITY.md](SECURITY.md) or contact the development team.

**Ready for production?** Review [Production Environment](#production-environment) section carefully!
