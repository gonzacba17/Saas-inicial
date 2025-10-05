#!/bin/bash

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_pre_remediation_${TIMESTAMP}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DRY_RUN=${DRY_RUN:-true}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_banner() {
    echo "======================================================"
    echo "  SECRETS REMEDIATION SCRIPT - EMERGENCY RESPONSE"
    echo "======================================================"
    echo "  Timestamp: $(date)"
    echo "  Mode: $([ "$DRY_RUN" = "true" ] && echo 'DRY RUN' || echo 'PRODUCTION')"
    echo "======================================================"
    echo ""
}

preflight_checks() {
    log_info "Running pre-flight checks..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Aborting."
        exit 1
    fi
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository. Aborting."
        exit 1
    fi
    
    if ! git diff-index --quiet HEAD --; then
        log_warn "You have uncommitted changes. These will be backed up."
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed. Aborting."
        exit 1
    fi
    
    log_info "Pre-flight checks passed ✓"
}

create_backup() {
    log_info "Creating backup in ${BACKUP_DIR}..."
    
    mkdir -p "${BACKUP_DIR}"
    
    git bundle create "${BACKUP_DIR}/repo_backup.bundle" --all
    
    if [ -f .env.production.secure ]; then
        cp -p .env.production.secure "${BACKUP_DIR}/"
    fi
    
    if [ -f docker-compose.secrets.yml ]; then
        cp -p docker-compose.secrets.yml "${BACKUP_DIR}/"
    fi
    
    git diff > "${BACKUP_DIR}/uncommitted_changes.patch" 2>/dev/null || true
    git diff --cached > "${BACKUP_DIR}/staged_changes.patch" 2>/dev/null || true
    
    log_info "Backup created successfully in ${BACKUP_DIR}/ ✓"
    log_warn "IMPORTANT: Store this backup securely and delete after verification!"
}

scan_for_secrets() {
    log_info "Scanning for exposed secrets in repository..."
    
    echo ""
    echo "Files containing potential secrets:"
    echo "-----------------------------------"
    
    find . -type f \( -name "*.env*" -o -name "*secret*" -o -name "*credential*" \) \
        ! -path "./node_modules/*" \
        ! -path "./backend/venv/*" \
        ! -path "./.git/*" \
        ! -path "./${BACKUP_DIR}/*" \
        ! -name "*.example" \
        ! -name "secrets.py" \
        ! -name "secrets_service.py" \
        2>/dev/null | while read -r file; do
        echo "  - $file"
    done
    
    echo ""
}

remove_from_history() {
    local file_path=$1
    
    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would remove from history: $file_path"
        return
    fi
    
    log_warn "Removing from Git history: $file_path"
    
    if command -v git-filter-repo &> /dev/null; then
        git filter-repo --path "$file_path" --invert-paths --force
    else
        log_warn "git-filter-repo not found, using filter-branch (slower)"
        git filter-branch --force --index-filter \
            "git rm --cached --ignore-unmatch $file_path" \
            --prune-empty --tag-name-filter cat -- --all
    fi
}

remediate_production_env() {
    log_info "Remediating .env.production.secure..."
    
    if [ ! -f .env.production.secure ]; then
        log_warn ".env.production.secure not found in working directory"
        return
    fi
    
    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would remove .env.production.secure from repository"
        return
    fi
    
    git rm --cached .env.production.secure 2>/dev/null || true
    
    remove_from_history ".env.production.secure"
    
    log_info "✓ .env.production.secure removed from repository"
}

cleanup_git() {
    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would cleanup Git repository"
        return
    fi
    
    log_info "Cleaning up Git repository..."
    
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    
    log_info "✓ Git cleanup completed"
}

validate_remediation() {
    log_info "Validating remediation..."
    
    echo ""
    echo "Checking for sensitive files in current commit:"
    if git ls-files | grep -E "\.env\.production\.secure|docker-compose\.secrets\.yml" > /dev/null 2>&1; then
        log_error "Sensitive files still tracked in repository!"
        git ls-files | grep -E "\.env\.production\.secure|docker-compose\.secrets\.yml"
        return 1
    else
        log_info "✓ No sensitive files in current commit"
    fi
    
    echo ""
    echo "Checking .gitignore coverage:"
    if grep -q "\.env\.production\.secure" .gitignore && \
       grep -q "docker-compose\.secrets\.yml" .gitignore; then
        log_info "✓ Sensitive files properly ignored"
    else
        log_warn "Sensitive files not in .gitignore - adding now..."
        if [ "$DRY_RUN" = "false" ]; then
            echo "" >> .gitignore
            echo ".env.production.secure" >> .gitignore
            echo "docker-compose.secrets.yml" >> .gitignore
        fi
    fi
    
    echo ""
}

show_next_steps() {
    echo ""
    echo "======================================================"
    echo "  NEXT STEPS"
    echo "======================================================"
    echo ""
    echo "1. VERIFY BACKUP:"
    echo "   → Check ${BACKUP_DIR}/ contains all expected files"
    echo ""
    echo "2. ROTATE ALL SECRETS (see ROTATION_CHECKLIST.md):"
    echo "   → JWT_SECRET"
    echo "   → DATABASE_PASSWORD"
    echo "   → REDIS_PASSWORD"
    echo "   → MERCADOPAGO_ACCESS_TOKEN"
    echo "   → OPENAI_API_KEY"
    echo ""
    echo "3. FORCE PUSH (if not dry run):"
    echo "   → COORDINATE WITH TEAM FIRST!"
    echo "   → git push origin main --force"
    echo "   → All team members must: git pull --rebase"
    echo ""
    echo "4. MONITOR:"
    echo "   → Check application logs for auth failures"
    echo "   → Verify all services reconnect successfully"
    echo ""
    echo "5. SECURE BACKUP:"
    echo "   → Move ${BACKUP_DIR}/ to secure location"
    echo "   → DELETE after 30 days retention period"
    echo ""
    echo "======================================================"
}

main() {
    show_banner
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "RUNNING IN DRY RUN MODE - No changes will be made"
        log_warn "Set DRY_RUN=false to execute actual remediation"
        echo ""
    fi
    
    preflight_checks
    
    create_backup
    
    scan_for_secrets
    
    remediate_production_env
    
    cleanup_git
    
    validate_remediation
    
    show_next_steps
    
    if [ "$DRY_RUN" = "true" ]; then
        echo ""
        log_info "DRY RUN COMPLETE - Review output above"
        log_info "To execute: DRY_RUN=false ./remediate_secrets.sh"
    else
        echo ""
        log_info "REMEDIATION COMPLETE"
        log_warn "Remember to ROTATE ALL SECRETS and FORCE PUSH!"
    fi
}

main "$@"
