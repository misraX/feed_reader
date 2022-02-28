[![Build Status](https://travis-ci.org/misraX/feed_reader.svg?branch=main)](https://travis-ci.org/misraX/feed_reader)
[![codecov](https://codecov.io/gh/misraX/feed_reader/branch/main/graph/badge.svg?token=k8C9e5Of1P)](https://codecov.io/gh/misraX/feed_reader)

#### Prerequisite:

1. docker and docker-compose.
2. virtualenv.
3. python 3.10 (Tested against python 3.8, 3.9).
6. Bash

### Installation:

Production build Using docker-compose [nginx, uwsgi, postgresql, redis, django]:

       # clone the repo
       $ git clone git@github.com:misraX/feed_reader.git
       $ cd feed_reader
       $ bash ./scripts/init.sh
       $ docker-compose up -d --build

Then head to: `http://localhost/api/v1/docs/` Swagger docs and play around

### Load Fixtures

The bellow will populate the system with feed, feed_items, and users

```ipython
In [1]: from apps.feed_parser.http import parse_feed

In [2]: from apps.feed.tests.factories import FeedFactory

In [4]: with transaction.atomic():
   ...:     for feed in FeedFactory.create_batch(8):
   ...:         parse_feed(feed)

```

The loaded feeds are actual live feeds, as follows, the list exists in `apps.feed.test.factories.FEED_LIST`

```python
FEED_LIST = [
    {
        'name': 'front-end-feed-codrops',
        'url': 'https://tympanus.net/codrops/feed/'},
    {
        'name': 'front-end-feed-css-tricks',
        'url': 'https://css-tricks.com/feed/'},
    {
        'name': 'front-end-feed-dev.to',
        'url': 'https://dev.to/feed'},
    {
        'name': 'front-end-feed-tutsplus',
        'url': 'https://code.tutsplus.com/posts.atom'},
    {
        'name': 'front-end-feed-hnrss',
        'url': 'https://hnrss.org/frontpage'},
    {
        'name': 'front-end-feed-hackernoon',
        'url': 'https://hackernoon.com/feed'},
    {
        'name': 'front-end-feed-sitepoint',
        'url': 'https://www.sitepoint.com/feed/'
    },
    {
        'name': 'front-end-feed-smashingmagazine',
        'url': 'https://www.smashingmagazine.com/feed',
    },
    {
        'name': 'Algemeen',
        'url': 'http://www.nu.nl/rss/Algemeen',
    },
    {
        'name': 'tweakers',
        'url': 'https://feeds.feedburner.com/tweakers/mixed',
    },
]
```

### Testing

`docker-compose exec django python manage.py test`

coverage report

` docker-compose exec django bash -c "coverage run manage.py test && coverage report -m"`

### API:

API documentations:

`coreapi` with _swagger_ `/api/v1/docs/`.

**Consuming endpoint using curl:**

- Register user:

`curl -X POST "http://localhost/api/v1/auth/register" -H  "accept: application/json" -H  "Content-Type: application/json"  -d "{ \"email\": \"user@example.com\", \"username\": \"string\", \"first_name\": \"string\", \"last_name\": \"string\", \"password\": \"string\"}"`

- Login user:

`curl -X POST "http://localhost/api/v1/auth/login" -H  "accept: application/json" -H  "Content-Type: application/json"  -d "{ \"username\": \"string\", \"password\": \"string\"}"`

will response with user token and expiry date, as follows:

```
{
  "expiry": "2022-02-28T04:00:10.070966Z",
  "token": "aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088"
}
```

- Follow/Subscribe to multiple feeds: "For the first time it will create a subscription, and then use PUT to update the
  existing subscription"<br>
  `curl -X POST "http://localhost/api/v1/subscribe/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json"  -d "{ \"feeds\": [3]}"`

- Follow/Update an existing subscription, one or many feeds<br>
  `curl -X PUT "http://localhost/api/v1/subscribe/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json"  -d "{ \"feeds\": [    12,13,14  ]}"`

- Unsubscribe/Update an existing subscription, one or many feeds<br>
  `curl -X PUT "http://localhost/api/v1/unsubscribe/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json" -d "{ \"feeds\": [    5  ]}"`

- List all feeds registered by them:<br>
  _**use user=pk filter**_<br>
  `curl -X GET "http://localhost/api/v1/feed/?user=1" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" `

- List feed items belonging to one feed:<br>
  _**use feed=pk filter**_<br>
  `curl -X GET "http://localhost/api/v1/feed-item/?feed=5" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" `

- Mark items as read: "For the first time it will create a reader profile, and then use `PUT` to update the existing
  reader"<br>
  `curl -X POST "http://localhost/api/v1/read/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json"  -d "{ \"items\": [    10  ]}"`

- Read/Update an existing reader profile<br>
  `curl -X PUT "http://localhost/api/v1/read/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json"  -d "{ \"items\": [    45  ]}"`

- Unread/Update an existing reader profile<br>
  `curl -X PUT "http://localhost/api/v1/unread/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json" -d "{ \"items\": [    47  ]}"`

- Filter read/unread feed items per feed and globally (e.g. get all unread items from all feeds or one feed in
  particular). Order the items by the date of the last update:<br>
  **_use read=true/True/1 filter read items_**<br>
  `curl -X GET "http://localhost/api/v1/feed-item/?read=true" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088"`<br>
  **_use order=created/-created, order by created date_**<br>
  `curl -X GET "http://localhost/api/v1/feed-item/?read=true&order=-created" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" `

- Force a feed update:

### Background tasks and Schedulers:

Using `celery` with `redis` to handle email notifications and background scheduler

### Authentication:

Default: `IsAuthenticated`

Token based authentication using [knox](https://github.com/James1345/django-rest-knox)

Knox authentication is token based, similar to the TokenAuthentication built in to DRF. However, it overcomes some
problems present in the default implementation:

> DRF tokens are limited to one per user. This does not facilitate securely signing in from multiple devices, as the token is shared. It also requires all devices to be logged out if a server-side logout is required (i.e. the token is deleted).
> Knox provides one token per call to the login view - allowing each client to have its own token which is deleted on the server side when the client logs out.
> Knox also provides an option for a logged in client to remove all tokens that the server has - forcing all clients to re-authenticate.
> DRF tokens are stored unencrypted in the database. This would allow an attacker unrestricted access to an account with a token if the database were compromised.
> Knox tokens are only stored in an encrypted form. Even if the database were somehow stolen, an attacker would not be able to log in with the stolen credentials.
> DRF tokens track their creation time, but have no inbuilt mechanism for tokens expiring. Knox tokens can have an expiry configured in the app settings (default is 10 hours.)

### Build and settings structure:

1.**Environment variables structure:**
---

`.env` for django

`docker/db/.env` for docker's postgres

leverage the usage of `django-environ` instead of `os.env`

2.**Docker compose structure:**
---

`docker-compse.yml`

**Services:**

- db: postgres <br>
- django: application server <br>
- redis: redis node <br>
- nginx: nginx reverse proxy

A modified version of wait_for_postgresql to handle docker delays
script [wait.py](https://github.com/agconti/wait-for-postgres/blob/master/wait_for_postgres/wait.py)
