#!/bin/bash
# Daily backups of every site (database + public and private files).
# Optional off-site copy with restic when RESTIC_REPOSITORY is set
# (S3, Backblaze B2, SFTP... see https://restic.readthedocs.io).
set -euo pipefail

INTERVAL="${BACKUP_INTERVAL_SECONDS:-86400}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
cd /home/frappe/frappe-bench

while true; do
	echo "[backup] $(date -Is) starting"
	bench --site all backup --with-files
	find sites/*/private/backups -type f -mtime +"$RETENTION_DAYS" -delete

	if [ -n "${RESTIC_REPOSITORY:-}" ]; then
		restic snapshots >/dev/null 2>&1 || restic init
		restic backup sites/*/private/backups --tag labqubit
		restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
	fi

	echo "[backup] $(date -Is) done, next run in ${INTERVAL}s"
	sleep "$INTERVAL"
done
