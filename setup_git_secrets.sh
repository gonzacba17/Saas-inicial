#!/bin/bash

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "======================================================"
echo "  GIT-SECRETS & PRE-COMMIT HOOKS SETUP"
echo "======================================================"
echo ""

check_python() {
    log_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is required but not installed."
        exit 1
    fi
    log_info "✓ Python3 found: $(python3 --version)"
}

check_pip() {
    log_info "Checking pip installation..."
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        log_error "pip is required but not installed."
        exit 1
    fi
    log_info "✓ pip found"
}

install_pre_commit() {
    log_info "Installing pre-commit framework..."
    
    if command -v pre-commit &> /dev/null; then
        log_info "✓ pre-commit already installed: $(pre-commit --version)"
    else
        pip3 install pre-commit || python3 -m pip install pre-commit
        log_info "✓ pre-commit installed"
    fi
}

install_git_secrets() {
    log_info "Checking git-secrets installation..."
    
    if command -v git-secrets &> /dev/null; then
        log_info "✓ git-secrets already installed"
        return
    fi
    
    log_warn "git-secrets not found. Attempting installation..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install git-secrets
            log_info "✓ git-secrets installed via Homebrew"
        else
            log_warn "Homebrew not found. Install manually from: https://github.com/awslabs/git-secrets"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -d "$HOME/git-secrets" ]; then
            cd "$HOME/git-secrets" && git pull
        else
            git clone https://github.com/awslabs/git-secrets.git "$HOME/git-secrets"
        fi
        cd "$HOME/git-secrets" && sudo make install
        log_info "✓ git-secrets installed"
    else
        log_warn "Manual installation required for git-secrets"
        log_warn "Visit: https://github.com/awslabs/git-secrets"
    fi
}

setup_git_secrets_hooks() {
    log_info "Setting up git-secrets hooks..."
    
    if ! command -v git-secrets &> /dev/null; then
        log_warn "Skipping git-secrets configuration (not installed)"
        return
    fi
    
    git secrets --install -f 2>/dev/null || true
    
    git secrets --register-aws
    
    if [ -f .git-secrets-patterns ]; then
        while IFS= read -r pattern; do
            if [[ ! "$pattern" =~ ^# ]] && [[ -n "$pattern" ]]; then
                git secrets --add "$pattern" 2>/dev/null || true
            fi
        done < .git-secrets-patterns
        log_info "✓ Custom patterns loaded from .git-secrets-patterns"
    fi
    
    git secrets --add --allowed '.*\.example$'
    git secrets --add --allowed 'CHANGE_THIS'
    git secrets --add --allowed 'YOUR_PRODUCTION'
    git secrets --add --allowed 'sk-your-openai'
    git secrets --add --allowed 'APP_USR_YOUR'
    
    log_info "✓ git-secrets configured"
}

setup_pre_commit_hooks() {
    log_info "Setting up pre-commit hooks..."
    
    if [ ! -f .pre-commit-config.yaml ]; then
        log_error ".pre-commit-config.yaml not found"
        exit 1
    fi
    
    pre-commit install
    pre-commit install --hook-type pre-push
    
    log_info "Initializing detect-secrets baseline..."
    detect-secrets scan --baseline .secrets.baseline 2>/dev/null || \
        pip3 install detect-secrets && detect-secrets scan --baseline .secrets.baseline
    
    log_info "✓ Pre-commit hooks installed"
}

test_hooks() {
    log_info "Testing hooks configuration..."
    
    echo ""
    echo "Running pre-commit on all files (this may take a moment)..."
    if pre-commit run --all-files; then
        log_info "✓ All pre-commit checks passed"
    else
        log_warn "Some checks failed - please review and fix"
        echo ""
        echo "Common fixes:"
        echo "  - Run: pre-commit run --all-files"
        echo "  - Commit the automatic fixes"
    fi
}

update_gitignore() {
    log_info "Updating .gitignore..."
    
    GITIGNORE_ENTRIES=(
        ""
        "# Prevent committing production secrets"
        ".env.production"
        ".env.production.secure"
        ".env.local"
        ".env.staging"
        "docker-compose.secrets.yml"
        ""
        "# Pre-commit"
        ".secrets.baseline"
    )
    
    for entry in "${GITIGNORE_ENTRIES[@]}"; do
        if ! grep -qF "$entry" .gitignore 2>/dev/null; then
            echo "$entry" >> .gitignore
        fi
    done
    
    log_info "✓ .gitignore updated"
}

show_summary() {
    echo ""
    echo "======================================================"
    echo "  SETUP COMPLETE"
    echo "======================================================"
    echo ""
    echo "Installed components:"
    echo "  ✓ pre-commit framework"
    echo "  ✓ Pre-commit hooks (trailing whitespace, yaml checks, etc.)"
    echo "  ✓ detect-secrets (baseline created)"
    [ -x "$(command -v git-secrets)" ] && echo "  ✓ git-secrets with custom patterns"
    echo ""
    echo "What happens now:"
    echo "  • Every commit is scanned for secrets automatically"
    echo "  • Production .env files are blocked"
    echo "  • Private keys are detected"
    echo "  • Code formatting is enforced (black, flake8)"
    echo ""
    echo "Testing the hooks:"
    echo "  $ echo 'password=SuperSecret123' > test.txt"
    echo "  $ git add test.txt"
    echo "  $ git commit -m 'test'"
    echo "  → Should be BLOCKED by hooks"
    echo ""
    echo "Bypass (emergency only):"
    echo "  $ git commit --no-verify -m 'message'"
    echo "  ⚠️  Use with extreme caution!"
    echo ""
    echo "Update hooks:"
    echo "  $ pre-commit autoupdate"
    echo ""
    echo "======================================================"
}

main() {
    cd "$(git rev-parse --show-toplevel)"
    
    check_python
    check_pip
    install_pre_commit
    install_git_secrets
    update_gitignore
    setup_git_secrets_hooks
    setup_pre_commit_hooks
    test_hooks
    show_summary
    
    log_info "🎉 Git security hooks setup complete!"
}

main "$@"
