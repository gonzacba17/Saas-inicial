# 🔄 CI/CD Workflows - Documentación Completa

## 📋 Índice

1. [Visión General](#visión-general)
2. [Workflows Implementados](#workflows-implementados)
3. [Configuración de Branch Protection](#configuración-de-branch-protection)
4. [Dependabot](#dependabot)
5. [Troubleshooting](#troubleshooting)

---

## Visión General

Nuestra arquitectura de CI/CD implementa un enfoque **Security-First** con 4 workflows principales que se ejecutan en paralelo para proporcionar feedback rápido y garantizar la calidad y seguridad del código.

### 🎯 Objetivos

- ⏱️ **Feedback rápido**: < 10 minutos para PRs pequeños
- 🔒 **Seguridad total**: 100% de PRs escaneados
- 📊 **Calidad enforced**: Coverage mínimo 70%
- 🚫 **Zero vulnerabilities**: Imposible mergear código con vulnerabilidades críticas
- 📈 **Alta confiabilidad**: > 95% pipeline reliability

---

## Workflows Implementados

### 1. 🔒 Security Scan (`security-scan.yml`)

**Trigger**: Push, PR, Semanal (domingos), Manual

**Jobs**:

#### 🔍 secret-scan
- **TruffleHog**: Escaneo de secretos verificados
- **detect-secrets**: Escaneo adicional de patrones
- **Timeout**: 10 minutos
- **Falla si**: Detecta secretos expuestos

#### 📦 dependency-scan
- **Backend**: pip-audit + Safety Check
- **Frontend**: npm audit + Snyk (opcional)
- **Matrix**: [backend, frontend]
- **Timeout**: 15 minutos

#### 🛡️ sast-scan
- **Bandit**: Python security linter
- **Semgrep**: Multi-language SAST
- **CodeQL**: GitHub native analysis
- **Permissions**: security-events: write
- **Timeout**: 20 minutos

#### 🐳 docker-scan
- **Trivy**: Container vulnerability scanner
- **Grype**: Additional scanning layer
- **Matrix**: [backend, frontend]
- **Exit code 1**: Si encuentra HIGH/CRITICAL
- **Timeout**: 20 minutos

#### 📊 security-summary
- Descarga todos los artifacts
- Genera reporte consolidado
- Comenta en PR con resultados
- **Runs**: Siempre (even if previous jobs fail)

**Artifacts generados**:
- `secret-scan-results`
- `dependency-scan-{backend|frontend}`
- `bandit-sast-report`
- `grype-scan-{backend|frontend}`

---

### 2. 🐍 Backend CI (`backend-ci.yml`)

**Trigger**: Push/PR en `backend/**`

**Jobs**:

#### 🎨 code-quality
- **Black**: Code formatting check
- **isort**: Import sorting validation
- **Flake8**: Style guide enforcement (max-line-length: 100)
- **MyPy**: Type checking (continue-on-error)
- **Pylint**: Advanced static analysis (continue-on-error)

#### 🧪 unit-tests
- **Framework**: pytest + pytest-cov
- **Database**: SQLite in-memory
- **Coverage**: xml + html + term-missing
- **Upload**: Codecov (flags: backend-unit)
- **Artifacts**: JUnit XML + HTML report

#### 🔗 integration-tests
- **Services**: PostgreSQL 15 + Redis 7
- **Database**: Full PostgreSQL setup
- **Migrations**: Alembic upgrade head
- **Coverage**: Combined with unit tests
- **Upload**: Codecov (flags: backend-integration)

#### 📊 coverage-check
- **Needs**: [unit-tests, integration-tests]
- **Threshold**: 70% minimum (enforced)
- **Status**: continue-on-error (por ahora)

**Configuración de Services**:
```yaml
postgres:
  image: postgres:15-alpine
  env:
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password_never_use_in_prod
    POSTGRES_DB: test_saas_db
  health-check: pg_isready
  
redis:
  image: redis:7-alpine
  health-check: redis-cli ping
```

---

### 3. ⚛️ Frontend CI (`frontend-ci.yml`)

**Trigger**: Push/PR en `frontend/**`

**Jobs**:

#### 🎨 lint
- **ESLint**: Max warnings = 0
- **Prettier**: Format validation
- **Files**: `src/**/*.{ts,tsx,js,jsx,json,css}`

#### 📘 typecheck
- **TypeScript**: tsc --noEmit
- **Pretty output**: Colored errors

#### 🧪 test
- **Framework**: Jest + React Testing Library
- **Coverage**: Full coverage report
- **Upload**: Codecov (flags: frontend)
- **Workers**: 2 (para CI speed)

#### 🏗️ build
- **Production build**: npm run build
- **Bundle check**: Warn si > 500KB
- **Artifacts**: Upload dist/

**Bundle Size Check**:
```bash
SIZE_KB=$(du -k dist/ | cut -f1)
if [ $SIZE_KB -gt 512 ]; then
  echo "⚠️ Warning: Bundle exceeds 500KB"
fi
```

---

### 4. ✅ PR Quality Gate (`pr-checks.yml`)

**Trigger**: PR opened, synchronize, reopened

**Jobs**:

#### 📋 validate-pr

**PR Title Convention**:
```
Formato: tipo(scope): descripción

Tipos válidos:
- feat: Nueva funcionalidad
- fix: Bug fix
- docs: Documentación
- style: Formato, no afecta código
- refactor: Refactoring
- test: Tests
- chore: Tareas de mantenimiento
- perf: Performance
- ci: CI/CD
- security: Seguridad

Ejemplos:
✅ feat(auth): add JWT refresh
✅ fix(db): migration issue
✅ security(api): prevent SQL injection
❌ added new feature
❌ Fix bug
```

**PR Description**:
- Debe existir (no vacía)
- Debe contener secciones: ## Changes | ## Descripción | ## What

**Breaking Changes**:
- Detecta palabras clave: "BREAKING CHANGE", "BREAKING"
- Marca warning en PR

**Conventional Commits**:
- Valida commits individuales
- Uses: wagoid/commitlint-github-action@v5

#### 🔍 analyze-changes

**Changed Files Analysis**:
- Detecta cambios en: backend/**, frontend/**, docker-compose*, .github/workflows/**

**Sensitive Files Check**:
```bash
SENSITIVE_PATTERNS=(.env .pem .key .p12 credentials secret)
```

**Test Coverage Requirements**:
- Si cambia código → Debe haber cambios en tests
- Warning si no hay tests correspondientes

#### ✅ all-checks
- Verifica que todos los jobs previos pasaron
- Falla si algún check falló
- Required para merge

---

## Configuración de Branch Protection

### Main Branch Protection Rules

**Path**: GitHub → Settings → Branches → Add rule

```yaml
Branch name pattern: main

✅ Require a pull request before merging
  ✅ Require approvals: 1
  ✅ Dismiss stale reviews
  ✅ Require review from Code Owners

✅ Require status checks to pass before merging
  ✅ Require branches to be up to date
  
  Required checks:
    - 🔒 Security Scan / secret-scan
    - 🔒 Security Scan / dependency-scan (backend)
    - 🔒 Security Scan / dependency-scan (frontend)
    - 🔒 Security Scan / sast-scan
    - 🔒 Security Scan / docker-scan (backend)
    - 🔒 Security Scan / docker-scan (frontend)
    - 🐍 Backend CI / code-quality
    - 🐍 Backend CI / unit-tests
    - 🐍 Backend CI / integration-tests
    - ⚛️ Frontend CI / lint
    - ⚛️ Frontend CI / typecheck
    - ⚛️ Frontend CI / test
    - ⚛️ Frontend CI / build
    - ✅ PR Quality Gate / all-checks

✅ Include administrators

✅ Restrict who can push to matching branches
  - Only: CI/CD bot, Release manager
```

### Develop Branch Protection Rules

Similar a main, pero:
- Approvals: 1 (puede ser el mismo autor para features)
- No incluir administrators en restricción
- Permitir force push para maintainers

---

## Dependabot

**Archivo**: `.github/dependabot.yml`

### Configuración Backend (Python)
```yaml
- package-ecosystem: "pip"
  directory: "/backend"
  schedule:
    interval: "weekly"
    day: "monday"
    time: "09:00"
  open-pull-requests-limit: 5
  labels: ["dependencies", "backend", "security"]
  commit-message:
    prefix: "chore(deps)"
```

### Configuración Frontend (npm)
```yaml
- package-ecosystem: "npm"
  directory: "/frontend"
  schedule:
    interval: "weekly"
    day: "monday"
    time: "09:00"
  open-pull-requests-limit: 5
  labels: ["dependencies", "frontend", "security"]
```

### Configuración GitHub Actions
```yaml
- package-ecosystem: "github-actions"
  directory: "/"
  schedule:
    interval: "monthly"
  labels: ["dependencies", "ci"]
```

**Auto-merge Dependabot PRs** (opcional):
```bash
gh pr merge --auto --squash <PR_NUMBER>
```

---

## Troubleshooting

### 🔴 Security Scan Failures

#### TruffleHog encontró secretos
```bash
# Solución 1: Rotar secretos inmediatamente
# Solución 2: Reescribir historia git
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret" \
  --prune-empty --tag-name-filter cat -- --all
```

#### pip-audit / Safety fallan
```bash
# Ver vulnerabilidades
pip-audit --desc

# Actualizar paquetes
pip install --upgrade <package>

# Si no hay fix disponible
pip-audit --ignore-vuln VULN-ID
```

#### Trivy encuentra vulnerabilidades en Docker
```bash
# Actualizar imagen base
FROM python:3.11-slim  # → python:3.11.7-slim

# Ver detalles
trivy image --severity HIGH,CRITICAL <image>
```

---

### 🔴 Backend CI Failures

#### Black formatting fails
```bash
cd backend
black app/
```

#### isort fails
```bash
cd backend
isort app/
```

#### Tests fallan
```bash
# Ejecutar localmente con mismo setup
docker-compose -f docker-compose.test.yml up -d
pytest tests/ -v
```

#### Coverage < 70%
```bash
# Ver qué falta cubrir
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

### 🔴 Frontend CI Failures

#### ESLint errors
```bash
cd frontend
npm run lint -- --fix
```

#### TypeScript errors
```bash
cd frontend
npx tsc --noEmit
# Fix type errors manualmente
```

#### Build fails
```bash
# Verificar variables de entorno
cat .env.production

# Build local
npm run build
```

---

### 🔴 PR Quality Gate Failures

#### PR Title no cumple convención
**Ejemplos correctos**:
```
feat(auth): add JWT refresh token
fix(api): correct user validation
docs(readme): update setup instructions
```

#### Sin descripción
Agregar al PR:
```markdown
## Changes
- Added feature X
- Fixed bug Y

## Testing
- Manual testing completed
- Unit tests added

## Breaking Changes
None
```

#### Falta tests
- Agregar tests correspondientes a los cambios
- O agregar comentario explicando por qué no se necesitan

---

## 📊 Métricas y Monitoreo

### KPIs del Pipeline

| Métrica | Target | Actual |
|---------|--------|--------|
| Feedback time (PR pequeño) | < 10 min | Monitor |
| PRs escaneados | 100% | ✅ |
| Coverage mínimo | 70% | Enforced |
| Pipeline reliability | > 95% | Monitor |
| Security vulnerabilities blocked | 100% | ✅ |

### Dashboard de CI/CD

**GitHub Actions**: https://github.com/gonzacba17/Saas-inicial/actions

**Codecov**: https://codecov.io/gh/gonzacba17/Saas-inicial

**Dependabot**: https://github.com/gonzacba17/Saas-inicial/security/dependabot

---

## 🔧 Mantenimiento

### Actualización de Workflows

1. Editar `.github/workflows/<workflow>.yml`
2. Crear PR con cambios
3. Validar en PR checks
4. Merge a main

### Agregar nuevo check requerido

1. Modificar workflow
2. Actualizar branch protection rules
3. Documentar en este archivo

### Deshabilitar temporalmente un check

```yaml
jobs:
  check-name:
    if: false  # Deshabilitar temporalmente
```

---

## 📚 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
- [CodeQL](https://codeql.github.com/docs/)
- [Trivy](https://aquasecurity.github.io/trivy/)
- [Semgrep](https://semgrep.dev/docs/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Última actualización**: 2025-10-05  
**Versión**: 2.1.0  
**Autor**: DevOps Team
