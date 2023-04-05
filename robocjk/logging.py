import logging
import traceback


class ThrottleFilter(logging.Filter):
    def __init__(self, timeout=3600):
        super().__init__()
        self.timeout = timeout

    def filter(self, record):
        try:
            from django.core.cache import caches

            cache = caches["logging"]
            if record.exc_info:
                exc_type = record.exc_info[0]
                exc_value = record.exc_info[1]
                exc_traceback = exc_value.__traceback__
                lastframe = traceback.extract_tb(exc_traceback)[-1]
                key = (
                    "logging.ThrottleFilter "
                    f"{exc_type.__name__} "
                    f"{lastframe.filename} "
                    f"{lastframe.lineno} "
                    f"{lastframe.name}"
                )
                if cache.get(key):
                    return False
                cache.set(key, True, self.timeout)
        except Exception:
            pass
        return True
