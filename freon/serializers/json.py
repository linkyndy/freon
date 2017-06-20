from __future__ import absolute_import
try:
    import simplejson as json
except ImportError:
    import json

from freon.serializers.base import BaseSerializer


class JsonSerializer(BaseSerializer):
    def dumps(self, data):
        return json.dumps(data)

    def loads(self, data):
        return json.loads(data)
