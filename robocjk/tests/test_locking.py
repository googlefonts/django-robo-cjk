# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase

from robocjk.locking import decode_lock_key, encode_lock_key
from robocjk.models import Project, Font, CharacterGlyph

import fsutil


class LockingTestCase(TestCase):

    @classmethod
    def read_glif_data(cls, path):
        glifpath = fsutil.join_path(__file__, 'test_models_data', path)
        glifdata = fsutil.read_file(glifpath)
        return glifdata

    def setUp(self):
        self._password = 'admin'
        self._user = User.objects.create_superuser('admin', 'admin@admin.com', self._password)
        self._client = Client()
        self._client.login(
            username=self._user.username,
            password=self._password,
        )
        self._project = Project.objects.create(
            name='My Font Family',
        )
        self._font = Font.objects.create(
            project=self._project,
            name='My Font',
        )
        self._character_glyph = CharacterGlyph.objects.create(
            font=self._font,
            data=self.read_glif_data('characterGlyph/uni4E_25.glif'),
        )

    def tearDown(self):
        pass

    def test_encode_decode(self):
        now = datetime.now()
        lock_key = encode_lock_key(
            user=self._user,
            glif=self._character_glyph,
            date=now,
        )
        # print(lock_key)
        data = decode_lock_key(lock_key)
        # print(data)
        expected_data = {
            'user_id': self._user.id,
            'glif_type': 'CharacterGlyph',
            'glif_id': self._character_glyph.id,
            'date': now.isoformat(),
        }

    def test_encode_idempotency(self):
        now = datetime.now()
        lock_key_1 = encode_lock_key(
            user=self._user,
            glif=self._character_glyph,
            date=now,
        )
        lock_key_2 = encode_lock_key(
            user=self._user,
            glif=self._character_glyph,
            date=now,
        )
        self.assertEqual(lock_key_1, lock_key_2)
