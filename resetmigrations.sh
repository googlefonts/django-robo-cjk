#!/bin/bash
# https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

APP=$1

if [ -z "$APP" ]; then
    APP="robocjk"
fi

source migrate.sh $APP

python manage.py migrate --fake $APP zero
python manage.py showmigrations $APP

find . -path "./$APP/migrations/*.py" -not -name "__init__.py" -delete
find . -path "./$APP/migrations/*.pyc"  -delete
python manage.py showmigrations $APP

python manage.py makemigrations $APP
python manage.py migrate $APP --fake-initial
python manage.py showmigrations $APP

source restart.sh