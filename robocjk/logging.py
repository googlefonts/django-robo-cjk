import hashlib
import logging


class ThrottleFilter(logging.Filter):
    def __init__(self, timeout=3600):
        super().__init__()
        self.timeout = timeout

    def filter(self, record):
        try:
            from django.core.cache import caches

            cache = caches["logging"]
            message = record.getMessage()
            key = hashlib.md5(message.encode("utf-8")).hexdigest()
            if cache.get(key):
                return False
            cache.set(key, True, self.timeout)
        except Exception:
            pass
        return True
