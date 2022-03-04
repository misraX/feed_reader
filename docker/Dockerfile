FROM python:3.10.2
ENV PYTHONUNBUFFERED 1

WORKDIR /srv/web

COPY ./ /srv/web/
RUN apt-get update \
        && apt-get install -y --no-install-recommends cron \
     	&& rm -rf /var/lib/apt/lists/* \
        && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt
