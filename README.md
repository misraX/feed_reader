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

### API:

API documentations: `coreapi` with _swagger_ `/api/v1/docs/`.

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

- Create Feed:<br>
`curl -X POST "http://localhost/api/v1/feed/" -H  "accept: application/json" -H  "Authorization: Token 5c92f93d2a4ccc097f3b7a90098e78e3bdd86a0f227955a292476047cbdfbf15" -H  "Content-Type: application/json" -d "{  \"name\": \"tweakers\",  \"url\": \"https://feeds.feedburner.com/tweakers/mixed\"}"`

- Follow/Update an existing subscription, one or many feeds<br>
  `curl -X PUT "http://localhost/api/v1/subscribe/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json"  -d "{ \"feeds\": [    12,13,14  ]}"`

- Unsubscribe/Update an existing subscription, one or many feeds<br>
  `curl -X PUT "http://localhost/api/v1/unsubscribe/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" -H  "Content-Type: application/json" -d "{ \"feeds\": [    5  ]}"`

- List all feeds registered by them:<br>
  _**use added_by_me=true/True/1 filter**_<br>
  `curl -X GET "http://localhost/api/v1/feed/added_by_me=True" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088" `

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

`curl -X GET "http://localhost/api/v1/force-update/1/" -H  "accept: application/json" -H  "Authorization: Token aa991fca86f8583e5ce4161a3284f6c799572705539be7a9293d7a76c6dd2088"`

### Load Fixtures

The bellow will populate the system with two feed , feed_items, and users

```ipython
In [1]: from apps.feed.tests.factories import FeedFactory
In [2]: FeedFactory.create_batch(8)
```

The loaded feeds are actual live feeds, as follows, the list exists in `apps.feed.test.factories.FEED_LIST`

```python
FEED_LIST = [
    {
        'name': 'Algemeen',
        'url': 'http://www.nu.nl/rss/Algemeen',
    },
    {
        'name': 'tweakers',
        'url': 'https://feeds.feedburner.com/tweakers/mixed',
    },
    {
        'name': 'front-end-feed-codrops',
        'url': 'https://tympanus.net/codrops/feed/',
    },
    {
        'name': 'front-end-feed-css-tricks',
        'url': 'https://css-tricks.com/feed/',
    },
    {
        'name': 'front-end-feed-dev.to',
        'url': 'https://dev.to/feed',
    },
    {
        'name': 'front-end-feed-tutsplus',
        'url': 'https://code.tutsplus.com/posts.atom',
    },
    {
        'name': 'front-end-feed-hnrss',
        'url': 'https://hnrss.org/frontpage',
    },
    {
        'name': 'front-end-feed-hackernoon',
        'url': 'https://hackernoon.com/feed',
    },
    {
        'name': 'front-end-feed-sitepoint',
        'url': 'https://www.sitepoint.com/feed/',
    },
    {
        'name': 'front-end-feed-smashingmagazine',
        'url': 'https://www.smashingmagazine.com/feed',
    },
]
```

### Testing

Run: `docker-compose exec django python manage.py test`

- Coverage report

` docker-compose exec django bash -c "coverage run manage.py test && coverage report -m"`

- Factories using factory_boy in `apps.feed.tests.factories`

Coverage:
```
Name                                        Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
apps/__init__.py                                0      0   100%
apps/accounts/__init__.py                       0      0   100%
apps/accounts/apps.py                           5      0   100%
apps/accounts/factories.py                      9      0   100%
apps/accounts/models.py                         9      0   100%
apps/accounts/serializers.py                   23      1    96%   24
apps/accounts/tests/__init__.py                 0      0   100%
apps/accounts/tests/test_views.py              28      0   100%
apps/accounts/urls.py                           6      0   100%
apps/accounts/views.py                         22      0   100%
apps/feed/__init__.py                           1      0   100%
apps/feed/admin.py                             11      0   100%
apps/feed/apps.py                               6      0   100%
apps/feed/exceptions.py                         4      0   100%
apps/feed/filters.py                           39      1    97%   44
apps/feed/management/__init__.py                0      0   100%
apps/feed/management/commands/__init__.py       0      0   100%
apps/feed/models.py                            71      3    96%   127, 151, 175
apps/feed/parser.py                           121     24    80%   43-45, 63, 65, 87-90, 115-117, 137-138, 148-154, 175-176, 186, 206-207
apps/feed/permission.py                         6      1    83%   9
apps/feed/serializers.py                       67     18    73%   74, 84-87, 99-102, 123-128, 137-139
apps/feed/signals.py                           14      0   100%
apps/feed/tasks.py                             42     10    76%   58, 92-100
apps/feed/tests/__init__.py                     0      0   100%
apps/feed/tests/factories.py                   38      0   100%
apps/feed/tests/test_models.py                 46      0   100%
apps/feed/tests/test_parser.py                 30      0   100%
apps/feed/tests/test_views.py                  78      0   100%
apps/feed/urls.py                              17      0   100%
apps/feed/views.py                             59      5    92%   40-42, 160-161
feed_reader/__init__.py                         2      0   100%
feed_reader/celery.py                           6      0   100%
feed_reader/settings.py                        40      0   100%
feed_reader/test_runner.py                      8      0   100%
feed_reader/urls.py                             9      0   100%
manage.py                                      12      2    83%   12-13
-------------------------------------------------------------------------
TOTAL                                         829     65    92%
```
### CACHING AND QUEUING

Memcached for caching and tasks concurrency<br>
RabbiMQ and Celery for asynchronous tasks<br>

### Background tasks and schedulers:

Using `celery` with `rabbitmq` along with `memcached` for results caching and lock handling

1. Failure backoff with exponential backoff with celery
2. Retries with celery retries on any exception thrown by the system
3. Concurrency locks with memcached to ensuring a task is only executed one at a time
4. Email notification with Django signal upon failure with a link to force-update
5. Scheduler using celery beat, with celery crontab periodic tasks

### Notification

User will get notified by email of the failures on any feed update, with a link to force update the feed

Sample email

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Feed https://hackernoon.com/feed failed to update
From: from@example.com
To: zward@example.net
Date: Fri, 04 Mar 2022 12:49:13 -0000
Message-ID: <164639815343.39.9929404946278173897@27f075e566ff>

Feed https://hackernoon.com/feed failed to update, you can still force updating the feed using  /api/v1/force-update/16/
-------------------------------------------------------------------------------
```

**NOTE** `filebased.EmailBackend` is used only for development purpose, any mail providers can be used/or push notification providers

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
`docker-compose.override.yml` for development and testing

**Services:**

- db: postgres <br>
- django: application server <br>
- rabbitmq: memcached node <br>
- memcached: memcached node <br>
- nginx: nginx reverse proxy

A modified version of wait_for_postgresql to handle docker delays
script [wait.py](https://github.com/agconti/wait-for-postgres/blob/master/wait_for_postgres/wait.py)
