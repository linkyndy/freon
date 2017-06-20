from __future__ import absolute_import
try:
    import cPickle as pickle
except ImportError:
    import pickle

from freon.serializers.base import BaseSerializer


class PickleSerializer(BaseSerializer):
    def dumps(self, data):
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

    def loads(self, data):
        return pickle.loads(data)
