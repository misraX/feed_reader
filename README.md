[![Build Status](https://travis-ci.org/misraX/feed_reader.svg?branch=main)](https://travis-ci.org/misraX/feed_reader)
[![codecov](https://codecov.io/gh/misraX/feed_reader/branch/master/graph/badge.svg)](https://codecov.io/gh/misraX/feed_reader)

#### Prerequisite:

1. docker and docker-compose.
2. virtualenv.
3. python 3.9 (Tested against python 3.8).
6. Bash

### Installation:

Production build Using docker-compose [nginx, uwsgi, postgresql, redis, django]:

       # clone the repo
       $ git clone git@github.com:misraX/feed_reader.git
       $ cd feed_reader
       $ bash ./scripts/init.sh
       $ docker-compose up -d --build

Then head to: `http://localhost/api/v1/docs/`


### Testing

`docker-compose exec django python manage.py test`

coverage report

` docker-compose exec django bash -c "coverage run manage.py test && coverage report -m"`

### API:

API documentations:

`coreapi` with _swagger_ `/api/v1/docs/`.

**Consuming endpoint using httpie:**

Installing httpie:

`pip install httpie`

- Register user:

`http POST http://localhost:9000/api/v1/auth/register username=misrax email=testuser@test.com password=mypassword`

- Login user:

` http POST http://localhost:9000/api/v1/auth/login username=misrax password=mypassword`

will response with user token example: `{ "token": "71d5818eb2cf2ab6c464664b129484b316e48f0c6506dca7bfe2b1fdec1c2c33" }`

- Follow and unfollow multiple feeds:

- List all feeds registered by them:

- List feed items belonging to one feed:

- Mark items as read:

- Filter read/unread feed items per feed and globally (e.g. get all unread items from all feeds or one feed in particular). Order the items by the date of the last update:

- Force a feed update:

### Background tasks and Schedulers:

Using `celery` with `redis` to handle email notifications and background scheduler

### Permissions:

Default: `IsAuthenticated`

Custom:

- `ObjectOwnerPermission`: Custom Permission to allow only owner of the object to access their data

### Authentication:

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

A modified version of wait_for_postgresql to handle docker delays script [wait.py](https://github.com/agconti/wait-for-postgres/blob/master/wait_for_postgres/wait.py)

### URLs

- /api/v1/auth/login      apps.accounts.views.LoginView   accounts-login <br>
- /api/v1/auth/logout     knox.views.LogoutView   accounts-logout <br>
- /api/v1/auth/logout-all knox.views.LogoutAllView        accounts-logout_all <br>
- /api/v1/auth/register   apps.accounts.views.RegisterView        accounts-register <br>
- /api/v1/docs/   drf_yasg.views.SchemaView       schema-swagger-ui <br>
- /api/v1/feed-item/      apps.feed.views.FeedItemViewSet feed-item-list <br>
- /api/v1/feed/   apps.feed.views.FeedViewSet     feed-list <br>
- /api/v1/feed/<pk>/      apps.feed.views.FeedViewSet     feed-detail <br>
- /api/v1/read/   apps.feed.views.ReadViewSet     feed-subscriber-list <br>
- /api/v1/read/<pk>/      apps.feed.views.ReadViewSet     feed-subscriber-detail <br>
- /api/v1/subscribe/      apps.feed.views.SubscribeViewSet        feed-subscriber-list <br>
- /api/v1/subscribe/<pk>/ apps.feed.views.SubscribeViewSet        feed-subscriber-detail <br>
- /api/v1/unread/<pk>/    apps.feed.views.UnReadViewSet   feed-unsubscribe-detail <br>
- /api/v1/unsubscribe/<pk>/       apps.feed.views.UnSubscribeViewSet      feed-unsubscribe-detail <br>
- /api/v1/user/feed-items/        apps.feed.views.UserFeedItemViewSet     feed-item-user-list <br>
- /api/v1/user/feeds/     apps.feed.views.UserFeedViewSet feed-user-list <br>
