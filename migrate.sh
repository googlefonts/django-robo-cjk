#!/bin/bash

APP=$1

if [ -z "$APP" ]; then
    APP="robocjk"
fi

python manage.py makemigrations $APP
python manage.py migrate $APP

source restart.sh
