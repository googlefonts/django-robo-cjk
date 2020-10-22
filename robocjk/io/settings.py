# -*- coding: utf-8 -*-

import re


GIT_REPOSITORIES_PATH = '/root/.rcjks'

GIT_SSH_REPOSITORY_PATTERN = r'git\@github\.com\:([\w\-\_]+){1}\/([\w\-\_]+){1}\.git'
GIT_SSH_REPOSITORY_RE = re.compile(GIT_SSH_REPOSITORY_PATTERN)
