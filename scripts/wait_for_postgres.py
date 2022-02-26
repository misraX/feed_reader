from __future__ import annotations

import logging
from time import sleep
from time import time

import environ
import psycopg2

# modified  version of https://github.com/agconti/wait-for-postgres
# to use envrion instead of os.env

root = environ.Path(__file__) - 2
env = environ.Env(
    POSTGRES_CHECK_TIMEOUT=(int, 30), POSTGRES_CHECK_INTERVAL=(
        int, 1,
    ),
)

env.read_env(f'{root}/.env')

db_config = env.db()

check_timeout = env('POSTGRES_CHECK_TIMEOUT', 30)
check_interval = env('POSTGRES_CHECK_INTERVAL', 1)
interval_unit = 'second' if check_interval == 1 else 'seconds'

config = {
    'dbname': db_config['NAME'],
    'user': db_config['USER'],
    'password': db_config['PASSWORD'],
    'host': db_config['HOST'],
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def pg_isready(host, user, password, dbname):
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**vars())
            logger.info('Postgres is ready! ✨ 💅')
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.info(
                f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}...",
            )
            sleep(check_interval)

    logger.error(
        f'We could not connect to Postgres within {check_timeout} seconds.',
    )
    return False


pg_isready(**config)
