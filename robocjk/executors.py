# -*- coding: utf-8 -*-

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from multiprocessing import BoundedSemaphore


class BoundedProcessPoolExecutor(ProcessPoolExecutor):

    def __init__(self, max_workers=None):
        super(BoundedProcessPoolExecutor, self).__init__(max_workers)
        self.semaphore = BoundedSemaphore(max_workers)

    def acquire(self):
        self.semaphore.acquire()

    def release(self, *args, **kwargs):
        self.semaphore.release()

    def submit(self, fn, *args, **kwargs):
        self.acquire()
        try:
            future = super(BoundedProcessPoolExecutor, self).submit(fn, *args, **kwargs)
            future.add_done_callback(self.release)
            return future
        except BrokenProcessPool as error:
            # print('BrokenProcessPool')
            self.release()
            return None
