import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings import get_secret_key


class SettingsSecurityTests(SimpleTestCase):
    def test_missing_secret_key_fails_fast(self):
        with patch.dict(os.environ, {"DJANGO_SECRET_KEY": ""}):
            with self.assertRaises(ImproperlyConfigured):
                get_secret_key()

    def test_example_secret_key_fails_fast(self):
        with patch.dict(
            os.environ,
            {"DJANGO_SECRET_KEY": "replace-with-a-long-random-secret"},
        ):
            with self.assertRaises(ImproperlyConfigured):
                get_secret_key()

    def test_configured_secret_key_is_returned(self):
        with patch.dict(os.environ, {"DJANGO_SECRET_KEY": "test-key-not-for-production"}):
            self.assertEqual(get_secret_key(), "test-key-not-for-production")
