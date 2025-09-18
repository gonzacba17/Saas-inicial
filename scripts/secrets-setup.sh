#!/bin/bash

# Secrets Management Setup Script
# Configures secrets management for different environments

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SECRETS_DIR="$PROJECT_ROOT/secrets"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [backend] [command]"
    echo ""
    echo "Backends:"
    echo "  environment  - Use environment variables (default)"
    echo "  file         - Use local files (development)"
    echo "  vault        - Use HashiCorp Vault (production)"
    echo "  aws          - Use AWS Secrets Manager (production)"
    echo ""
    echo "Commands:"
    echo "  setup        - Initialize secrets backend"
    echo "  create       - Create a new secret"
    echo "  get          - Get a secret value"
    echo "  list         - List all secrets"
    echo "  backup       - Backup all secrets"
    echo "  restore      - Restore secrets from backup"
    echo "  migrate      - Migrate secrets between backends"
    echo ""
    echo "Examples:"
    echo "  $0 file setup"
    echo "  $0 environment create database"
    echo "  $0 vault get api_keys"
}

# Function to setup file backend
setup_file_backend() {
    print_status "Setting up file-based secrets backend..."
    
    # Create secrets directory
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
    
    # Create .gitignore for secrets
    echo "*" > "$SECRETS_DIR/.gitignore"
    echo "!.gitignore" >> "$SECRETS_DIR/.gitignore"
    
    # Create example secrets
    create_example_secrets_file
    
    print_success "File backend setup completed at: $SECRETS_DIR"
}

# Function to setup environment backend
setup_environment_backend() {
    print_status "Setting up environment variables backend..."
    
    # Create .env.secrets file
    cat > "$PROJECT_ROOT/.env.secrets" << 'EOF'
# Secrets Configuration
SECRETS_BACKEND=environment

# Database Secrets
SAAS_SECRET_DATABASE={"host":"localhost","port":"5432","user":"saasuser","password":"securepassword","database":"saas_cafeterias"}

# JWT Secrets
SAAS_SECRET_JWT={"secret_key":"your-super-secret-jwt-key-64-characters-minimum","algorithm":"HS256"}

# API Keys
SAAS_SECRET_API_KEYS={"mercadopago_token":"your-mercadopago-token","openai_key":"your-openai-api-key","smtp_password":"your-smtp-password"}

# Encryption Keys
SAAS_SECRET_ENCRYPTION={"key":"your-encryption-key-32-bytes","salt":"your-salt-16-bytes"}
EOF
    
    print_success "Environment backend setup completed"
    print_warning "Edit .env.secrets with your actual secrets"
    print_warning "Source the file: source .env.secrets"
}

# Function to setup Vault backend
setup_vault_backend() {
    print_status "Setting up HashiCorp Vault backend..."
    
    local vault_url="${VAULT_URL:-http://localhost:8200}"
    local vault_token="$VAULT_TOKEN"
    
    if [ -z "$vault_token" ]; then
        print_error "VAULT_TOKEN environment variable is required"
        exit 1
    fi
    
    print_status "Testing Vault connection to $vault_url..."
    
    # Test Vault connection
    if command -v curl &> /dev/null; then
        response=$(curl -s -H "X-Vault-Token: $vault_token" "$vault_url/v1/sys/health" || echo "failed")
        if [[ "$response" == *"\"initialized\":true"* ]]; then
            print_success "Vault connection successful"
        else
            print_error "Cannot connect to Vault at $vault_url"
            exit 1
        fi
    else
        print_warning "curl not found, skipping connection test"
    fi
    
    # Create example secrets in Vault
    create_example_secrets_vault "$vault_url" "$vault_token"
    
    print_success "Vault backend setup completed"
}

# Function to setup AWS backend
setup_aws_backend() {
    print_status "Setting up AWS Secrets Manager backend..."
    
    local aws_region="${AWS_REGION:-us-east-1}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is required but not installed"
        exit 1
    fi
    
    # Test AWS connection
    print_status "Testing AWS connection..."
    if aws sts get-caller-identity > /dev/null 2>&1; then
        print_success "AWS connection successful"
    else
        print_error "Cannot connect to AWS. Check your credentials"
        exit 1
    fi
    
    # Create example secrets in AWS
    create_example_secrets_aws "$aws_region"
    
    print_success "AWS Secrets Manager backend setup completed"
}

# Function to create example secrets for file backend
create_example_secrets_file() {
    print_status "Creating example secrets..."
    
    # Database secret
    cat > "$SECRETS_DIR/database.json" << 'EOF'
{
  "host": "localhost",
  "port": "5432",
  "user": "saasuser",
  "password": "securepassword",
  "database": "saas_cafeterias"
}
EOF
    chmod 600 "$SECRETS_DIR/database.json"
    
    # JWT secret
    cat > "$SECRETS_DIR/jwt.json" << 'EOF'
{
  "secret_key": "your-super-secret-jwt-key-64-characters-minimum",
  "algorithm": "HS256"
}
EOF
    chmod 600 "$SECRETS_DIR/jwt.json"
    
    # API keys
    cat > "$SECRETS_DIR/api_keys.json" << 'EOF'
{
  "mercadopago_token": "your-mercadopago-token",
  "openai_key": "your-openai-api-key",
  "smtp_password": "your-smtp-password"
}
EOF
    chmod 600 "$SECRETS_DIR/api_keys.json"
    
    # Encryption keys
    cat > "$SECRETS_DIR/encryption.json" << 'EOF'
{
  "key": "your-encryption-key-32-bytes",
  "salt": "your-salt-16-bytes"
}
EOF
    chmod 600 "$SECRETS_DIR/encryption.json"
    
    print_success "Example secrets created in $SECRETS_DIR"
}

# Function to create example secrets in Vault
create_example_secrets_vault() {
    local vault_url="$1"
    local vault_token="$2"
    
    print_status "Creating example secrets in Vault..."
    
    # Database secret
    curl -s -H "X-Vault-Token: $vault_token" \
         -H "Content-Type: application/json" \
         -X POST \
         -d '{"data":{"host":"localhost","port":"5432","user":"saasuser","password":"securepassword","database":"saas_cafeterias"}}' \
         "$vault_url/v1/secret/data/database" > /dev/null
    
    # JWT secret
    curl -s -H "X-Vault-Token: $vault_token" \
         -H "Content-Type: application/json" \
         -X POST \
         -d '{"data":{"secret_key":"your-super-secret-jwt-key-64-characters-minimum","algorithm":"HS256"}}' \
         "$vault_url/v1/secret/data/jwt" > /dev/null
    
    # API keys
    curl -s -H "X-Vault-Token: $vault_token" \
         -H "Content-Type: application/json" \
         -X POST \
         -d '{"data":{"mercadopago_token":"your-mercadopago-token","openai_key":"your-openai-api-key","smtp_password":"your-smtp-password"}}' \
         "$vault_url/v1/secret/data/api_keys" > /dev/null
    
    print_success "Example secrets created in Vault"
}

# Function to create example secrets in AWS
create_example_secrets_aws() {
    local aws_region="$1"
    
    print_status "Creating example secrets in AWS Secrets Manager..."
    
    # Database secret
    aws secretsmanager create-secret \
        --region "$aws_region" \
        --name "saas/database" \
        --secret-string '{"host":"localhost","port":"5432","user":"saasuser","password":"securepassword","database":"saas_cafeterias"}' \
        > /dev/null 2>&1 || print_warning "Database secret may already exist"
    
    # JWT secret
    aws secretsmanager create-secret \
        --region "$aws_region" \
        --name "saas/jwt" \
        --secret-string '{"secret_key":"your-super-secret-jwt-key-64-characters-minimum","algorithm":"HS256"}' \
        > /dev/null 2>&1 || print_warning "JWT secret may already exist"
    
    # API keys
    aws secretsmanager create-secret \
        --region "$aws_region" \
        --name "saas/api_keys" \
        --secret-string '{"mercadopago_token":"your-mercadopago-token","openai_key":"your-openai-api-key","smtp_password":"your-smtp-password"}' \
        > /dev/null 2>&1 || print_warning "API keys secret may already exist"
    
    print_success "Example secrets created in AWS Secrets Manager"
}

# Function to create a new secret
create_secret() {
    local secret_name="$1"
    local backend="${2:-environment}"
    
    if [ -z "$secret_name" ]; then
        echo "Usage: $0 $backend create <secret_name>"
        exit 1
    fi
    
    print_status "Creating secret: $secret_name"
    
    # Get secret values from user
    echo "Enter secret values (key=value format, empty line to finish):"
    declare -A secret_data
    
    while true; do
        read -p "Key=Value (or empty to finish): " input
        if [ -z "$input" ]; then
            break
        fi
        
        if [[ "$input" == *"="* ]]; then
            key="${input%%=*}"
            value="${input#*=}"
            secret_data["$key"]="$value"
        else
            print_warning "Invalid format. Use key=value"
        fi
    done
    
    # Convert to JSON
    json_data="{"
    first=true
    for key in "${!secret_data[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            json_data+=","
        fi
        json_data+="\"$key\":\"${secret_data[$key]}\""
    done
    json_data+="}"
    
    # Save based on backend
    case $backend in
        file)
            echo "$json_data" > "$SECRETS_DIR/$secret_name.json"
            chmod 600 "$SECRETS_DIR/$secret_name.json"
            ;;
        environment)
            echo "SAAS_SECRET_${secret_name^^}='$json_data'" >> "$PROJECT_ROOT/.env.secrets"
            ;;
        *)
            print_error "Creating secrets for $backend backend not implemented in this script"
            print_status "Use the Python secrets service API instead"
            ;;
    esac
    
    print_success "Secret $secret_name created"
}

# Function to get a secret
get_secret() {
    local secret_name="$1"
    local backend="${2:-environment}"
    
    if [ -z "$secret_name" ]; then
        echo "Usage: $0 $backend get <secret_name>"
        exit 1
    fi
    
    case $backend in
        file)
            if [ -f "$SECRETS_DIR/$secret_name.json" ]; then
                cat "$SECRETS_DIR/$secret_name.json"
            else
                print_error "Secret $secret_name not found"
            fi
            ;;
        environment)
            env_var="SAAS_SECRET_${secret_name^^}"
            value="${!env_var}"
            if [ -n "$value" ]; then
                echo "$value"
            else
                print_error "Secret $secret_name not found in environment"
            fi
            ;;
        *)
            print_error "Getting secrets for $backend backend not implemented in this script"
            print_status "Use the Python secrets service API instead"
            ;;
    esac
}

# Function to list secrets
list_secrets() {
    local backend="${1:-environment}"
    
    case $backend in
        file)
            if [ -d "$SECRETS_DIR" ]; then
                print_status "Secrets in file backend:"
                for file in "$SECRETS_DIR"/*.json; do
                    if [ -f "$file" ]; then
                        basename "$file" .json
                    fi
                done
            else
                print_warning "No secrets directory found"
            fi
            ;;
        environment)
            print_status "Secrets in environment backend:"
            env | grep "^SAAS_SECRET_" | cut -d= -f1 | sed 's/^SAAS_SECRET_//' | tr '[:upper:]' '[:lower:]'
            ;;
        *)
            print_error "Listing secrets for $backend backend not implemented in this script"
            print_status "Use the Python secrets service API instead"
            ;;
    esac
}

# Function to backup secrets
backup_secrets() {
    local backend="${1:-environment}"
    local backup_file="secrets_backup_$(date +%Y%m%d_%H%M%S).json"
    
    print_status "Backing up secrets from $backend backend..."
    
    case $backend in
        file)
            if [ -d "$SECRETS_DIR" ]; then
                # Create JSON backup
                echo "{" > "$backup_file"
                first=true
                for file in "$SECRETS_DIR"/*.json; do
                    if [ -f "$file" ]; then
                        secret_name=$(basename "$file" .json)
                        if [ "$first" = true ]; then
                            first=false
                        else
                            echo "," >> "$backup_file"
                        fi
                        echo -n "  \"$secret_name\": " >> "$backup_file"
                        cat "$file" >> "$backup_file"
                    fi
                done
                echo "" >> "$backup_file"
                echo "}" >> "$backup_file"
                
                print_success "Backup created: $backup_file"
            else
                print_error "No secrets directory found"
            fi
            ;;
        *)
            print_error "Backup for $backend backend not implemented in this script"
            print_status "Use the Python secrets service API instead"
            ;;
    esac
}

# Main execution
BACKEND="${1:-environment}"
COMMAND="${2:-setup}"

case $COMMAND in
    setup)
        case $BACKEND in
            environment) setup_environment_backend ;;
            file) setup_file_backend ;;
            vault) setup_vault_backend ;;
            aws) setup_aws_backend ;;
            *) print_error "Unknown backend: $BACKEND"; show_usage; exit 1 ;;
        esac
        ;;
    create)
        create_secret "$3" "$BACKEND"
        ;;
    get)
        get_secret "$3" "$BACKEND"
        ;;
    list)
        list_secrets "$BACKEND"
        ;;
    backup)
        backup_secrets "$BACKEND"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac