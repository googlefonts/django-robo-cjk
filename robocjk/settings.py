# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

import re


API_AUTH_TOKEN_EXPIRATION = {'days':1 } if settings.DEBUG else {'minutes':5}
API_RESPONSE_TIME_LIMIT = 0.4 if settings.DEBUG else 0.4

GIT_REPOSITORIES_PATH = '/root/.rcjks'

GIT_SSH_REPOSITORY_PATTERN = r'git\@github\.com\:([\w\-\_]+){1}\/([\w\-\_]+){1}\.git'
GIT_SSH_REPOSITORY_RE = re.compile(GIT_SSH_REPOSITORY_PATTERN)
GIT_SSH_REPOSITORY_URL_VALIDATOR = RegexValidator(GIT_SSH_REPOSITORY_PATTERN,
    _('Invalid repository URL - Expected .git repository SSH URL, eg. git@github.com:username/repository.git'))
