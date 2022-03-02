FROM python:3.10.2
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/web

COPY ./ /srv/web/

RUN pip install --no-cache-dir -r requirements.txt
