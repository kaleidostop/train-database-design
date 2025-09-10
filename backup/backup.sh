#!/bin/sh
set -ex

BACKUP_DIR=/backups
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

echo "Starting backup: $BACKUP_FILE"

pg_dump -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" | gzip > "$BACKUP_FILE"

echo "Backup finished."

ls -1t $BACKUP_DIR/db_backup_*.sql.gz | tail -n +$((BACKUP_RETENTION_COUNT+1)) | xargs -r rm --

echo "Old backups cleaned up. Keeping last $BACKUP_RETENTION_COUNT backups"