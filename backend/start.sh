#!/bin/bash

python manage.py collectstatic --noinput && python manage.py migrate app cart users
gunicorn --bind 0:8000 --workers=5 --threads=2 foodgram.wsgi:application