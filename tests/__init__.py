import unittest
from redislite.patch import patch_redis, unpatch_redis

from freon.cache import Cache


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        patch_redis()
        self.cache = Cache()

    def tearDown(self):
        unpatch_redis()
