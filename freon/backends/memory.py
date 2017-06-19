from __future__ import absolute_import
import glob
import os
import sortedsets
import time

from freon.backends.base import BaseBackend


class MemoryBackend(BaseBackend):
    def __init__(self, **kwargs):
        self.ttl_key = kwargs.pop('ttl_key', 'freon:cache:ttls')
        self.store = {}
        self.store[self.ttl_key] = SortedSet()

    def get_lock(self, name):
        return self.client.lock("%s_lock" % name, timeout=1)

    def get(self, key):
        value = self.store[key]
        expired = self.store[self.ttl_key][key] < time.time()
        return (value, expired)

    def set(self, key, value, ttl):
        self.store[key] = value
        self.store[self.ttl_key][key] = time.time() + ttl
        return True

    def delete(self, key):
        del self.store[key]
        del self.store[self.ttl_key][key]
        return True

    def exists(self, key):
        return key in self.store

    def get_expired(self):
        return self.store[self.ttl_key].by_score[0:time.time()]

    def get_by_ttl(self, ttl):
        return self.store[self.ttl_key].by_score[time.time():time.time() + ttl]
