#! /bin/bash
python manage.py makemigrations;
python manage.py migrate;
python manage.py load_csv;
python manage.py collectstatic --noinput;
gunicorn -b 0:8000 foodgram.wsgi;