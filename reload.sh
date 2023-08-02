#!/bin/bash

# remove all .pyc/.pyo files
# find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# run django checks
python manage.py check

# re-collect static files
# python manage.py collectstatic --clear --noinput --verbosity 0

# restart gunicorn (graceful reload)
source ../gunicorn/gunicorn reload
