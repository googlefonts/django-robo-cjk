import threading


def threaded(func):
    def wrapper(*args, **kwargs):
        func_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_thread.start()
        return func_thread

    return wrapper
