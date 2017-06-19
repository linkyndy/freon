from . import BaseTestCase

from freon.cache import Cache

from mock import Mock, patch
# class MockBackend(object)

class StringSerializer(object):
    def dumps(self, value):
        return str(value)

    def loads(self, value):
        return str(value)

class CacheTestCase(BaseTestCase):
    def setUp(self):
        self.cache = Cache()
        # Set a default string serializer for easier testing
        self.cache.serializer.dumps = lambda x: str(x)
        self.cache.serializer.loads = lambda x: str(x)


class GetTests(CacheTestCase):
    def test_with_existing_expired_key(self):
        self.cache.backend.get = lambda x: ('bar', True)
        assert self.cache.get('foo') == 'bar'

    def test_with_existing_not_expired_key(self):
        self.cache.backend.get = lambda x: ('bar', False)
        assert self.cache.get('foo') == 'bar'

    def test_with_not_existing_key(self):
        self.cache.backend.get = lambda x: (None, True)
        assert self.cache.get('foo') is None
