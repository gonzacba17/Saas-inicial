#!/bin/bash

# Database backup script for PostgreSQL
# This script creates automated backups with retention policy

set -e

# Configuration
DB_HOST="${POSTGRES_HOST:-db}"
DB_NAME="${POSTGRES_DB:-saas_cafeterias}"
DB_USER="${POSTGRES_USER:-saasuser}"
DB_PASSWORD="${POSTGRES_PASSWORD:-saaspass}"
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to create backup
create_backup() {
    log "Starting backup of database: $DB_NAME"
    
    # Create SQL backup
    PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        log "Backup created successfully: $BACKUP_FILE"
        
        # Compress backup
        gzip $BACKUP_FILE
        log "Backup compressed: ${BACKUP_FILE}.gz"
        
        # Create checksum
        md5sum "${BACKUP_FILE}.gz" > "${BACKUP_FILE}.gz.md5"
        log "Checksum created: ${BACKUP_FILE}.gz.md5"
        
    else
        log "ERROR: Backup failed!"
        exit 1
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days"
    
    find $BACKUP_DIR -name "backup_${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find $BACKUP_DIR -name "backup_${DB_NAME}_*.sql.gz.md5" -mtime +$RETENTION_DAYS -delete
    
    log "Old backups cleaned up"
}

# Function to verify backup
verify_backup() {
    local backup_file="${BACKUP_FILE}.gz"
    
    if [ -f "$backup_file" ]; then
        # Check if file is not empty
        if [ -s "$backup_file" ]; then
            log "Backup verification passed: $backup_file"
            return 0
        else
            log "ERROR: Backup file is empty: $backup_file"
            return 1
        fi
    else
        log "ERROR: Backup file not found: $backup_file"
        return 1
    fi
}

# Function to send notification (placeholder)
send_notification() {
    local status=$1
    local message=$2
    
    # TODO: Implement notification system (email, Slack, etc.)
    log "NOTIFICATION [$status]: $message"
}

# Main backup process
main() {
    log "=== Starting backup process ==="
    
    # Check if database is accessible
    PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -U $DB_USER -d $DB_NAME
    if [ $? -ne 0 ]; then
        log "ERROR: Database is not accessible"
        send_notification "ERROR" "Database backup failed - database not accessible"
        exit 1
    fi
    
    # Create backup
    create_backup
    
    # Verify backup
    if verify_backup; then
        log "Backup process completed successfully"
        send_notification "SUCCESS" "Database backup completed successfully"
    else
        log "ERROR: Backup verification failed"
        send_notification "ERROR" "Database backup failed verification"
        exit 1
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    log "=== Backup process finished ==="
}

# Run main function
main "$@"