FROM postgres:15

RUN apt-get update && apt-get install -y cron gettext-base dos2unix tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backup-entrypoint.sh .
RUN chmod +x backup-entrypoint.sh

COPY crontab.txt backup-cron.template

COPY backup.sh .
RUN chmod +x backup.sh  

CMD ["/app/backup-entrypoint.sh"]