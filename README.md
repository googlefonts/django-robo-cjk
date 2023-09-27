# django-robo-cjk

`django-robo-cjk` is the server-side engine based on `python` and `django` that serves the [robo-cjk](https://github.com/BlackFoundryCom/robo-cjk) RoboFont plugin and the [fontra-rcjk](https://github.com/googlefonts/fontra-rcjk) Fontra plugin.

Its purpose is to centralize and speed-up the design/development of CJK typefaces providing a whole set of APIs to manage `.rcjk` projects.

## Installation

### Requirements
- `Python >= 3.11` is necessary to use this project locally or remotely.
- `MySQL` *(we use this project with a MySQL database, but other databases can be used)*
- `Nginx` *(we use nginx as webserver in our remote environment)*
- `Gunicorn` *(we use gunicorn as appserver in our remote environment)*

### Setup
```bash
# create project directory
mkdir myrcjkfont && cd myrcjkfont

# create virtualenv and activate it
python -m venv venv && . venv/bin/activate

# clone repository
git clone https://github.com/googlefonts/django-robo-cjk.git src/ && cd src/

# upgrade pip
python -m pip install --upgrade pip

# install requirements
pip install -r requirements.txt

# install pre-commit to run formatters and linters
pre-commit install --install-hooks

# create environment settings file
mkdir conf && touch conf/env_settings
```

### Configuration
Add the following environment settings to `conf/env_settings` file and configure them:

```bash
ADMIN_NAME=""
ADMIN_EMAIL=""
DATABASE_ENGINE=""
DATABASE_NAME=""
DATABASE_USER=""
DATABASE_PASSWORD=""
DEBUG=True
DEBUG_TOOLBAR_SHOW=True
EMAIL_HOST="smtp.gmail.com"
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
GIT_REPOSITORIES_PATH="/your-path/.rcjks"
GIT_USER_EMAIL=""
GIT_USER_NAME=""
HASHIDS_SALT=""
JWT_SECRET=""
MEDIA_ROOT="/your-path/robocjk/public/media/"
ROBOCJK_EXPORT_CANCEL_TIMEOUT=120
ROBOCJK_EXPORT_QUERIES_PAGINATION_LIMIT=500
SECRET_KEY=""
SENTRY_DSN=""
SENTRY_ENVIRONMENT=""
STATIC_ROOT="/your-path/robocjk/public/static/"
TEST_API_HOST=""
TEST_API_USERNAME=""
TEST_API_PASSWORD=""
```

### Check
- Run `python manage.py check` 
- Run `python manage.py runserver`


## API

- [Globals](https://github.com/googlefonts/django-robo-cjk/edit/master/API.md#globals) 
- [Endpoints](https://github.com/googlefonts/django-robo-cjk/edit/master/API.md#endpoints)
- [Client](https://github.com/googlefonts/django-robo-cjk/edit/master/API.md#client)

## License
Released under [GNU General Public License v3.0](LICENSE).
