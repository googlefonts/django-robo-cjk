import re

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

GIT_SSH_REPOSITORY_PATTERN = r"git\@github\.com\:([\w\-\_]+){1}\/([\w\-\_]+){1}\.git"
GIT_SSH_REPOSITORY_RE = re.compile(GIT_SSH_REPOSITORY_PATTERN)


class GitSSHRepositoryURLValidator(RegexValidator):
    def __init__(self):
        super().__init__(
            regex=GIT_SSH_REPOSITORY_PATTERN,
            message=_(
                "Invalid repository URL - Expected .git repository SSH URL, eg. git@github.com:username/repository.git"
            ),
        )
