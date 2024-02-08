#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

# for debug
# python manage.py runserver 0.0.0.0:8000

# For production
gunicorn --bind 0.0.0.0:8000 --workers 4 auking.wsgi:application

$@