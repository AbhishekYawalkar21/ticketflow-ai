#!/bin/bash

echo "💾 Backing up database..."

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

docker-compose exec -T postgres pg_dump -U ticketflow ticketflow_db > "$BACKUP_FILE"

echo "✅ Backup saved to $BACKUP_FILE"