# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.test import TestCase

from robocjk.validators import GitSSHRepositoryURLValidator


class ValidatorsTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_git_ssh_repo_url_validator(self):
        validator = GitSSHRepositoryURLValidator()
        validator('git@github.com:BlackFoundryCom/django-robo-cjk.git')
        with self.assertRaises(ValidationError):
            validator('https://github.com/BlackFoundryCom/django-robo-cjk.git')
