#!/bin/bash

python manage.py check
# python manage.py collectstatic --clear --noinput --verbosity 0
source ~/scripts/gunicorn.sh restart
