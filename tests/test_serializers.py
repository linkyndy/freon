import pytest
import time

from freon.serializers.json import JsonSerializer
from freon.serializers.msgpack import MsgpackSerializer
from freon.serializers.pickle import PickleSerializer

from tests import BaseTestCase


class SerializeTests(BaseTestCase):
    def setUp(self):
        self.serializers = [JsonSerializer(), MsgpackSerializer(), PickleSerializer()]

    def test_string(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps('foobar')) == 'foobar'

    def test_complex_string(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps('fO0b@r ')) == 'fO0b@r '

    def test_list(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps(['foo', 'bar'])) == ['foo', 'bar']

    def test_dict(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps({'foo': 'bar'})) == {'foo': 'bar'}
