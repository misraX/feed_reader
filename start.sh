#!/bin/bash

python ./scripts/wait_for_postgres.py
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
uwsgi --ini uwsgi.ini
celery -A feed_reader multi stop worker1  \
    --pidfile="$HOME/run/celery/%n.pid" \
    --logfile="$HOME/log/celery/%n%I.log"

celery -A feed_reader multi start worker1  \
    --pidfile="$HOME/run/celery/%n.pid" \
    --logfile="$HOME/log/celery/%n%I.log"

tail -f /srv/web/logs/uwsgi-err.log
