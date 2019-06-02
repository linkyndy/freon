from __future__ import absolute_import
import glob
import os
import redis

from freon.backends.base import BaseBackend


class RedisBackend(BaseBackend):
    def __init__(self, host='localhost', port=6379, db=0, password=None, **kwargs):
        self.ttl_key = kwargs.pop('ttl_key', 'freon:cache:ttls')
        self.client = redis.StrictRedis(host=host, port=port, db=db,
                                        password=password, decode_responses=True,
                                        **kwargs)
        self.register_scripts()

    def get_lock(self, name):
        return self.client.lock("%s_lock" % name, timeout=1)

    def get(self, key):
        value, expired = self.run_script('get', keys=[key, self.ttl_key])
        return (value, bool(expired))

    def set(self, key, value, ttl):
        response = self.run_script('set', keys=[key, self.ttl_key], args=[value, ttl])
        return bool(response)

    def delete(self, key):
        response = self.run_script('delete', keys=[key, self.ttl_key])
        return bool(response)

    def exists(self, key):
        response = self.client.exists(key)
        return bool(response)

    def get_expired(self):
        return self.run_script('get_expired', keys=[self.ttl_key])

    def get_by_ttl(self, ttl):
        return self.run_script('get_by_ttl', keys=[self.ttl_key], args=[ttl])

    def register_scripts(self):
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')

        self._scripts = {}
        for filename in glob.glob(os.path.join(script_dir, '*.lua')):
            with open(filename, 'r') as f:
                script = self.client.register_script(f.read())
                name = os.path.splitext(os.path.basename(filename))[0]
                self._scripts[name] = script

    def run_script(self, name, keys=[], args=[]):
        return self._scripts[name](keys, args)
