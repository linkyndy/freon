from __future__ import absolute_import
import glob
import os
import threading
import time

from freon.backends.base import BaseBackend


class MemoryBackend(BaseBackend):
    def __init__(self, **kwargs):
        self.ttl_key = kwargs.pop('ttl_key', 'freon:cache:ttls')
        self.store = {}
        self.store[self.ttl_key] = {}

    def get_lock(self, _):
        return threading.Lock()

    def get(self, key):
        try:
            value = self.store[key]
            expired = self.store[self.ttl_key][key] < time.time()
            return (value, expired)
        except KeyError:
            return (None, True)

    def set(self, key, value, ttl):
        self.store[key] = value
        self.store[self.ttl_key][key] = time.time() + ttl
        return True

    def delete(self, key):
        try:
            del self.store[key]
            del self.store[self.ttl_key][key]
        except KeyError:
            pass
        return True

    def exists(self, key):
        return key in self.store

    def get_expired(self):
        return [key for key, expiration_time in self.store[self.ttl_key].items()
                if 0 <= expiration_time <= time.time()]

    def get_by_ttl(self, ttl):
        return [key for key, expiration_time in self.store[self.ttl_key].items()
                if time.time() <= expiration_time <= time.time() + ttl]
