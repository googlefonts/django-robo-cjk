import logging

from django.core import mail
from django.test import TestCase

logger = logging.getLogger(__name__)


class LoggingTestCase(TestCase):
    def test_error_mail_admins(self):
        logger.error("Test error mail admin handler.")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[-1].subject,
            "[development] ERROR: Test error mail admin handler.",
        )
        logger.error("Test another error mail admin handler.")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[-1].subject,
            "[development] ERROR: Test another error mail admin handler.",
        )
