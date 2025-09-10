#!/bin/sh
set -ex

touch /var/log/backup.log
chmod u=rw,g=r,o=r /var/log/backup.log

dos2unix /app/backup-cron.template

envsubst < /app/backup-cron.template > /etc/cron.d/backup-cron
chmod u=rw,g=r,o=r /etc/cron.d/backup-cron

exec cron -f