#!/usr/bin/env bash

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
done

alembic upgrade head

gunicorn app:app -w $WORKERS --worker-class=gevent --bind $API_HOST:$API_PORT
exec "$@"