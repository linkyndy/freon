import pytest
import time

from freon.serializers.json import JsonSerializer
from freon.serializers.msgpack import MsgpackSerializer
from freon.serializers.pickle import PickleSerializer

from tests import BaseTestCase


class BasicSerializeTests(BaseTestCase):
    def setUp(self):
        self.serializers = [JsonSerializer(), MsgpackSerializer(), PickleSerializer()]

    def test_string(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps('foobar')) == 'foobar'

    def test_complex_string(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps('fO0b@r ')) == 'fO0b@r '

    def test_integer(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps(1234)) == 1234

    def test_float(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps(12.34)) == 12.34

    def test_list(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps(['foo', 'bar'])) == ['foo', 'bar']

    def test_dict(self):
        for serializer in self.serializers:
            assert serializer.loads(serializer.dumps({'foo': 'bar'})) == {'foo': 'bar'}


def custom_encoder(obj):
    return {"foo": "bar"}


def custom_decoder(obj):
    return Baz()


class Baz(object):
    pass


class CustomSerializeTests(BaseTestCase):
    def setUp(self):
        self.serializers = [JsonSerializer(custom_encoder, custom_decoder),
                            MsgpackSerializer(custom_encoder, custom_decoder),
                            PickleSerializer(custom_encoder, custom_decoder)]

    def test_custom(self):
        for serializer in self.serializers:
            assert isinstance(serializer.loads(serializer.dumps(Baz())), Baz)
