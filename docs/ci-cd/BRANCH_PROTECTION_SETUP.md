# 🛡️ Guía de Configuración de Branch Protection

## 📋 Índice

1. [Visión General](#visión-general)
2. [Configuración para Main Branch](#configuración-para-main-branch)
3. [Configuración para Develop Branch](#configuración-para-develop-branch)
4. [Configuración de CODEOWNERS](#configuración-de-codeowners)
5. [Verificación](#verificación)

---

## Visión General

Branch Protection Rules aseguran que:
- ✅ Todo código pase por review
- ✅ Todos los checks de CI/CD pasen antes de merge
- ✅ No se pueda hacer push directo a branches protegidas
- ✅ Las políticas se apliquen incluso a administradores

---

## Configuración para Main Branch

### Paso 1: Acceder a Branch Protection Rules

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Branches**
3. Click en **Add branch protection rule**

### Paso 2: Configurar Pattern

```
Branch name pattern: main
```

### Paso 3: Require Pull Request

✅ **Require a pull request before merging**
- ✅ **Require approvals**: `1`
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require review from Code Owners** (si tienes CODEOWNERS configurado)
- ❌ **Require approval of the most recent reviewable push**

### Paso 4: Require Status Checks

✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**

**Status checks - Search and select these checks:**

#### Security Checks
```
Security Scan / secret-scan
Security Scan / dependency-scan (backend)
Security Scan / dependency-scan (frontend)
Security Scan / sast-scan
Security Scan / docker-scan (backend)
Security Scan / docker-scan (frontend)
Security Scan / security-summary
```

#### Backend Checks
```
Backend CI / code-quality
Backend CI / unit-tests
Backend CI / integration-tests
Backend CI / coverage-check
```

#### Frontend Checks
```
Frontend CI / lint
Frontend CI / typecheck
Frontend CI / test
Frontend CI / build
```

#### PR Quality Checks
```
PR Quality Gate / validate-pr
PR Quality Gate / analyze-changes
PR Quality Gate / all-checks
```

**Total: ~20 required checks**

### Paso 5: Configuraciones Adicionales

✅ **Require conversation resolution before merging**

✅ **Require signed commits** (opcional, recomendado para producción)

✅ **Include administrators**
- Esto asegura que ni siquiera los admins puedan saltarse las reglas

✅ **Restrict who can push to matching branches**
- Add: `ci-bot` (si existe)
- Add: `release-manager` (usuario autorizado)

❌ **Allow force pushes**
- NUNCA habilitar en main

❌ **Allow deletions**
- NUNCA habilitar en main

### Paso 6: Guardar Configuración

Click en **Create** o **Save changes**

---

## Configuración para Develop Branch

### Pattern
```
Branch name pattern: develop
```

### Diferencias vs Main

#### Require Pull Request
- ✅ **Require approvals**: `1`
- ❌ **Dismiss stale reviews**: Opcional
- ⚠️ **Require review from Code Owners**: Opcional

#### Status Checks
- Mismos checks que main

#### Configuraciones Adicionales
- ❌ **Include administrators**: Opcional
- ✅ **Restrict who can push**: Solo maintainers
- ⚠️ **Allow force pushes**: Solo para maintainers (cuidado!)
- ❌ **Allow deletions**: Nunca

---

## Configuración de CODEOWNERS

### Crear archivo .github/CODEOWNERS

```bash
# Backend code review
/backend/**                     @gonzacba17 @backend-team

# Frontend code review
/frontend/**                    @gonzacba17 @frontend-team

# CI/CD changes require DevOps review
/.github/workflows/**           @gonzacba17 @devops-team

# Security and infrastructure
/docker-compose*.yml            @gonzacba17 @devops-team
/monitoring/**                  @gonzacba17 @devops-team

# Database migrations require extra review
/backend/alembic/versions/**    @gonzacba17 @backend-team @dba-team

# Documentation
/docs/**                        @gonzacba17

# Root config files
/*.yml                          @gonzacba17 @devops-team
/*.json                         @gonzacba17
/.*                             @gonzacba17 @devops-team
```

### Configurar Team Permissions

1. **Settings → Manage access → Add teams**
2. Crear teams:
   - `backend-team` → Write access
   - `frontend-team` → Write access
   - `devops-team` → Maintain access
   - `dba-team` → Write access

---

## Configuración para Feature Branches

### Pattern Wildcard
```
Branch name pattern: feature/**
```

### Reglas más Flexibles
- ✅ **Require pull request**: Sí
- ✅ **Require approvals**: `0` o `1` (según preferencia)
- ✅ **Status checks**: Mismos que main
- ❌ **Include administrators**: No
- ❌ **Restrict who can push**: No
- ✅ **Allow force pushes**: Sí (solo en features)
- ❌ **Allow deletions**: No

---

## Configuración Avanzada

### Auto-merge para Dependabot

Si usas Dependabot, configura auto-merge:

```yaml
# .github/workflows/dependabot-auto-merge.yml
name: Dependabot Auto-merge

on:
  pull_request:
    branches: [ main, develop ]

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    
    steps:
      - name: Dependabot metadata
        id: metadata
        uses: dependabot/fetch-metadata@v1
        
      - name: Enable auto-merge for minor/patch updates
        if: steps.metadata.outputs.update-type == 'version-update:semver-minor' || steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{github.event.pull_request.html_url}}
          GITHUB_TOKEN: ${{secrets.GITHUB_TOKEN}}
```

### Rulesets (GitHub Rulesets - Nueva Feature)

GitHub Rulesets es el reemplazo moderno de Branch Protection Rules.

**Ventajas**:
- Aplica a múltiples branches con un solo ruleset
- Más granular y flexible
- Mejor UX

**Para activar**:
1. Settings → Rules → Rulesets → New ruleset
2. Target: `main`, `develop`, `release/**`
3. Configure rules (similar a branch protection)

---

## Configuración de Merge Queue (Opcional)

Para repos muy activos:

1. Settings → General → Pull Requests
2. ✅ **Enable merge queue**
3. **Merge method**: Squash
4. **Status checks**: Same as branch protection

**Beneficios**:
- Serializa merges automáticamente
- Evita race conditions
- Asegura que cada merge pase todos los tests

---

## Verificación

### Checklist de Verificación

#### Main Branch
- [ ] No se puede hacer push directo
- [ ] Requiere 1 aprobación mínimo
- [ ] Todos los checks de CI/CD son requeridos
- [ ] Code owners deben aprobar
- [ ] Administradores están incluidos en reglas
- [ ] Force push está deshabilitado
- [ ] Delete está deshabilitado

#### Develop Branch
- [ ] Requiere pull request
- [ ] Todos los checks pasan
- [ ] Configuración apropiada para colaboración

#### CODEOWNERS
- [ ] Archivo existe en `.github/CODEOWNERS`
- [ ] Teams están configurados
- [ ] Owners están asignados correctamente

### Test Manual

1. **Intentar push directo a main** (debe fallar):
   ```bash
   git checkout main
   echo "test" >> test.txt
   git add test.txt
   git commit -m "test direct push"
   git push origin main
   # ❌ Debe fallar con: "protected branch hook declined"
   ```

2. **Crear PR sin pasar checks** (debe bloquear merge):
   - Crear PR que falle algún check
   - Verificar que botón "Merge" esté deshabilitado

3. **Crear PR válido**:
   - Crear PR que pase todos los checks
   - Obtener aprobación requerida
   - Verificar que merge esté disponible

---

## Screenshots de Configuración

### Branch Protection Rule - Main

```
┌─────────────────────────────────────────────────────────┐
│ Branch protection rule                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Branch name pattern: main                              │
│                                                         │
│ ✅ Require a pull request before merging               │
│    ├── Required approvals: 1                           │
│    ├── ✅ Dismiss stale reviews                        │
│    └── ✅ Require review from Code Owners              │
│                                                         │
│ ✅ Require status checks to pass                       │
│    ├── ✅ Require branches to be up to date            │
│    └── Status checks:                                  │
│        ├── Security Scan / secret-scan                 │
│        ├── Security Scan / dependency-scan (backend)   │
│        ├── Security Scan / sast-scan                   │
│        ├── Backend CI / code-quality                   │
│        ├── Backend CI / unit-tests                     │
│        ├── Frontend CI / lint                          │
│        ├── Frontend CI / test                          │
│        └── ... (total ~20 checks)                      │
│                                                         │
│ ✅ Require conversation resolution                     │
│                                                         │
│ ✅ Include administrators                              │
│                                                         │
│ ✅ Restrict who can push                               │
│    └── ci-bot, release-manager                         │
│                                                         │
│ ❌ Allow force pushes                                  │
│                                                         │
│ ❌ Allow deletions                                     │
│                                                         │
│          [ Create ]  [ Cancel ]                        │
└─────────────────────────────────────────────────────────┘
```

---

## Rollback Plan

Si necesitas deshabilitar temporalmente las protecciones:

### Opción 1: Deshabilitar Rule Temporalmente
1. Settings → Branches
2. Click en la regla de `main`
3. Desmarcar las opciones necesarias
4. Save changes
5. ⚠️ **IMPORTANTE**: Re-habilitar ASAP

### Opción 2: Bypass con Admin Override
1. Solo para emergencias críticas
2. Requiere aprobación del CTO/Engineering Lead
3. Documentar en incident report
4. Crear task para fix post-incident

### Opción 3: Crear Branch de Emergency
```bash
git checkout -b emergency/hotfix-YYYY-MM-DD
# Hacer fix
# Crear PR a main
# Merge con admin override si es crítico
```

---

## Mantenimiento

### Actualizar Required Checks

Cuando agregues nuevos workflows:

1. Editar branch protection rule
2. Buscar nuevo check en "Status checks"
3. Marcar como required
4. Save changes

### Revisar Logs de Bypass

Mensualmente, revisar:
1. Settings → Branches → Rule insights
2. Verificar si hubo bypasses
3. Investigar razones
4. Actualizar políticas si es necesario

---

## Recursos

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [CODEOWNERS Syntax](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

---

**Última actualización**: 2025-10-05  
**Versión**: 1.0.0  
**Contacto**: DevOps Team
