import pytest
import redis
import time

from freon.backends.redis import RedisBackend

from tests import BaseTestCase


class RedisTestCase(BaseTestCase):
    def setUp(self):
        self.backend = RedisBackend(db=15, ttl_key='freon:cache:test_ttl')
        self.client = redis.StrictRedis(db=15, decode_responses=True)

    def tearDown(self):
        self.client.flushdb()

    def set_key(self, key, value, ttl=0):
        self.client.set(key, value)
        self.client.zadd('freon:cache:test_ttl', {key: time.time() + ttl})

    def assert_set(self, key, value, ttl):
        assert self.client.get(key) == value
        assert self.client.zscore('freon:cache:test_ttl', key) == pytest.approx(time.time() + ttl)

    def assert_deleted(self, key):
        assert self.client.get(key) is None
        assert self.client.zscore('freon:cache:test_ttl', key) is None


class GetTests(RedisTestCase):
    def test_with_existing_expired_key(self):
        self.set_key('foo', 'bar', -123)
        assert self.backend.get('foo') == ('bar', True)

    def test_with_existing_not_expired_key(self):
        self.set_key('foo', 'bar', 123)
        assert self.backend.get('foo') == ('bar', False)

    def test_with_not_existing_key(self):
        assert self.backend.get('foo') == (None, True)

    def test_returns_two_element_tuple(self):
        response = self.backend.get('foo')
        assert isinstance(response, tuple) is True
        assert len(response) == 2


class SetTests(RedisTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar', 123)
        self.backend.set('foo', 'baz', 1234)
        self.assert_set('foo', 'baz', 1234)

    def test_with_not_existing_key(self):
        self.backend.set('foo', 'bar', 1234)
        self.assert_set('foo', 'bar', 1234)

    def test_returns_true(self):
        assert self.backend.set('foo', 'baz', 1234) is True


class DeleteTests(RedisTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar')
        self.backend.delete('foo')
        self.assert_deleted('foo')

    def test_with_not_existing_key(self):
        self.backend.delete('foo')
        self.assert_deleted('foo')

    def test_returns_true(self):
        assert self.backend.delete('foo') is True


class ExistsTests(RedisTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar')
        assert self.backend.exists('foo') is True

    def test_with_not_existing_key(self):
        assert self.backend.exists('foo') is False


class GetExpiredTests(RedisTestCase):
    def test_with_expired_and_not_expired_key(self):
        self.set_key('foo', 'foo', -123)
        self.set_key('bar', 'bar', 123)
        assert self.backend.get_expired() == ['foo']


class GetByTtl(RedisTestCase):
    def test_with_expired_and_not_expired_key(self):
        self.set_key('foo', 'foo', -123)
        self.set_key('bar', 'bar', 123)
        self.set_key('baz', 'baz', 1234)
        # Python's time() precision is different than Redis' so we want to make
        # sure we include the right keys in the response
        assert self.backend.get_by_ttl(124) == ['bar']
