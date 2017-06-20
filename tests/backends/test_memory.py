import pytest
import time

from freon.backends.memory import MemoryBackend

from tests import BaseTestCase


class MemoryTestCase(BaseTestCase):
    def setUp(self):
        self.backend = MemoryBackend(ttl_key='freon:cache:test_ttl')

    def set_key(self, key, value, ttl=0):
        self.backend.store[key] = value
        self.backend.store['freon:cache:test_ttl'][key] = time.time() + ttl

    def assert_set(self, key, value, ttl):
        assert self.backend.store[key] == value
        assert self.backend.store['freon:cache:test_ttl'][key] == pytest.approx(time.time() + ttl)

    def assert_deleted(self, key):
        assert key not in self.backend.store
        assert key not in self.backend.store['freon:cache:test_ttl']


class GetTests(MemoryTestCase):
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


class SetTests(MemoryTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar', 123)
        self.backend.set('foo', 'baz', 1234)
        self.assert_set('foo', 'baz', 1234)

    def test_with_not_existing_key(self):
        self.backend.set('foo', 'bar', 1234)
        self.assert_set('foo', 'bar', 1234)

    def test_returns_true(self):
        assert self.backend.set('foo', 'baz', 1234) is True


class DeleteTests(MemoryTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar')
        self.backend.delete('foo')
        self.assert_deleted('foo')

    def test_with_not_existing_key(self):
        self.backend.delete('foo')
        self.assert_deleted('foo')

    def test_returns_true(self):
        assert self.backend.delete('foo') is True


class ExistsTests(MemoryTestCase):
    def test_with_existing_key(self):
        self.set_key('foo', 'bar')
        assert self.backend.exists('foo') is True

    def test_with_not_existing_key(self):
        assert self.backend.exists('foo') is False


class GetExpiredTests(MemoryTestCase):
    def test_with_expired_and_not_expired_key(self):
        self.set_key('foo', 'foo', -123)
        self.set_key('bar', 'bar', 123)
        assert self.backend.get_expired() == ['foo']


class GetByTtl(MemoryTestCase):
    def test_with_expired_and_not_expired_key(self):
        self.set_key('foo', 'foo', -123)
        self.set_key('bar', 'bar', 123)
        self.set_key('baz', 'baz', 1234)
        # Python's time() precision is different than Redis' so we want to make
        # sure we include the right keys in the response
        assert self.backend.get_by_ttl(124) == ['bar']
