from redislite.patch import patch_redis, unpatch_redis
import pytest
import time

from freon.backends.redis import RedisBackend

from . import BaseTestCase


class RedisTests(BaseTestCase):
    def setUp(self):
        patch_redis()
        self.backend = RedisBackend()

    def tearDown(self):
        self.backend.client.flushall()
        unpatch_redis()

    def set_key(self, key, value):
        self.backend.client.set(key, value)

    def assert_set(self, key, value, ttl):
        assert self.backend.client.get(key) == value
        assert self.backend.client.zscore('freon:ttls', key) == pytest.approx(time.time() + ttl)

    # def test_get_existing(self):
    #     self.backend.set('foo', 'bar', 1234)
    #     value = self.backend.get('foo')
    #     assert value == ('bar', False)

    def test_get_not_existing(self):
        value = self.backend.get('foo')
        assert value == (None, True)

    def test_set_with_existing_key(self):
        self.set_key('foo', 'bar')
        self.backend.set('foo', 'baz', 1234)
        self.assert_set('foo', 'baz', 1234)

    def test_set_with_not_existing_key(self):
        self.backend.set('foo', 'bar', 1234)
        self.assert_set('foo', 'bar', 1234)

    def test_exists_with_existing_key(self):
        self.set_key('foo', 'bar')
        assert self.backend.exists('foo') is True

    def test_exists_with_not_existing_key(self):
        assert self.backend.exists('foo') is False
