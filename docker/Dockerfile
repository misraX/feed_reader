FROM python:3.10.2
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/web

COPY ./ /srv/web/

RUN pip install --no-cache-dir -r requirements.txt

CMD python ./scripts/wait_for_postgres.py && python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && uwsgi --ini uwsgi.ini
