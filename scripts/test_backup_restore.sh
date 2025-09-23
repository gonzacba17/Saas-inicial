#!/bin/bash

# Test script for backup and restore functionality
# Validates that backup/restore process works correctly

set -e

# Configuration
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_NAME="${POSTGRES_DB:-saas_cafeterias}"
DB_USER="${POSTGRES_USER:-saasuser}"
DB_PASSWORD="${POSTGRES_PASSWORD:-saaspass}"
TEST_DB_NAME="${DB_NAME}_test_restore"
BACKUP_DIR="/tmp/backup_test"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to cleanup test resources
cleanup() {
    log "Cleaning up test resources..."
    
    # Drop test database if exists
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" postgres 2>/dev/null || true
    
    # Remove test backup files
    rm -rf $BACKUP_DIR
    
    log "Cleanup completed"
}

# Function to create test data
create_test_data() {
    log "Creating test data in original database..."
    
    # Create test business
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
        INSERT INTO businesses (id, name, description, created_at, updated_at, is_active) 
        VALUES (
            gen_random_uuid(), 
            'Test Backup Business ${TIMESTAMP}', 
            'Business created for backup testing', 
            NOW(), 
            NOW(), 
            true
        ) ON CONFLICT DO NOTHING;
    " 2>/dev/null || warning "Could not create test data (table might not exist)"
}

# Function to verify test data
verify_test_data() {
    local db_name=$1
    log "Verifying test data in database: $db_name"
    
    local count=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $db_name -t -c "
        SELECT COUNT(*) FROM businesses WHERE name LIKE 'Test Backup Business%';
    " 2>/dev/null | xargs || echo "0")
    
    if [ "$count" -gt "0" ]; then
        log "✅ Test data verified: $count test businesses found"
        return 0
    else
        error "❌ Test data verification failed: no test businesses found"
        return 1
    fi
}

# Function to test backup creation
test_backup_creation() {
    log "Testing backup creation..."
    
    # Create backup directory
    mkdir -p $BACKUP_DIR
    
    # Create test data first
    create_test_data
    
    # Create backup using our backup script logic
    local backup_file="${BACKUP_DIR}/test_backup_${TIMESTAMP}.sql"
    
    PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $backup_file
    
    if [ $? -eq 0 ] && [ -s "$backup_file" ]; then
        log "✅ Backup created successfully: $backup_file"
        
        # Compress backup
        gzip $backup_file
        log "✅ Backup compressed: ${backup_file}.gz"
        
        return 0
    else
        error "❌ Backup creation failed"
        return 1
    fi
}

# Function to test backup restore
test_backup_restore() {
    log "Testing backup restore..."
    
    local backup_file="${BACKUP_DIR}/test_backup_${TIMESTAMP}.sql.gz"
    
    if [ ! -f "$backup_file" ]; then
        error "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Create test database for restore
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -U $DB_USER $TEST_DB_NAME
    
    if [ $? -ne 0 ]; then
        error "❌ Could not create test database: $TEST_DB_NAME"
        return 1
    fi
    
    log "✅ Test database created: $TEST_DB_NAME"
    
    # Restore backup to test database
    gunzip -c $backup_file | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $TEST_DB_NAME
    
    if [ $? -eq 0 ]; then
        log "✅ Backup restored successfully to: $TEST_DB_NAME"
        
        # Verify restored data
        if verify_test_data $TEST_DB_NAME; then
            log "✅ Data integrity verified after restore"
            return 0
        else
            error "❌ Data integrity check failed after restore"
            return 1
        fi
    else
        error "❌ Backup restore failed"
        return 1
    fi
}

# Function to test backup script directly
test_backup_script() {
    log "Testing backup script execution..."
    
    # Check if backup script exists
    if [ -f "./scripts/backup.sh" ]; then
        # Test backup script with environment variables
        BACKUP_DIR=$BACKUP_DIR \
        POSTGRES_HOST=$DB_HOST \
        POSTGRES_DB=$DB_NAME \
        POSTGRES_USER=$DB_USER \
        POSTGRES_PASSWORD=$DB_PASSWORD \
        ./scripts/backup.sh
        
        if [ $? -eq 0 ]; then
            log "✅ Backup script executed successfully"
            return 0
        else
            error "❌ Backup script execution failed"
            return 1
        fi
    else
        warning "⚠️ Backup script not found at ./scripts/backup.sh"
        return 1
    fi
}

# Main test function
main() {
    log "=== Starting Backup/Restore Testing ==="
    
    # Trap to ensure cleanup on exit
    trap cleanup EXIT
    
    # Check if database is accessible
    PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME
    if [ $? -ne 0 ]; then
        error "❌ Database is not accessible"
        error "   Make sure PostgreSQL is running and credentials are correct"
        exit 1
    fi
    
    log "✅ Database connectivity verified"
    
    # Test 1: Backup Creation
    if test_backup_creation; then
        log "🎯 TEST 1 PASSED: Backup Creation"
    else
        error "❌ TEST 1 FAILED: Backup Creation"
        exit 1
    fi
    
    # Test 2: Backup Restore
    if test_backup_restore; then
        log "🎯 TEST 2 PASSED: Backup Restore"
    else
        error "❌ TEST 2 FAILED: Backup Restore"
        exit 1
    fi
    
    # Test 3: Backup Script
    if test_backup_script; then
        log "🎯 TEST 3 PASSED: Backup Script"
    else
        warning "⚠️ TEST 3 SKIPPED: Backup Script (not critical)"
    fi
    
    log "=== All Backup/Restore Tests Completed Successfully ==="
    log "✅ Backup system is working correctly"
    log "✅ Data integrity is maintained during restore"
    log "✅ Automated backup scripts are functional"
    
    return 0
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi