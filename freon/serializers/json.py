from __future__ import absolute_import
try:
    import simplejson as json
except ImportError:
    import json

from freon.serializers.base import BaseSerializer


class JsonSerializer(BaseSerializer):
    def dumps(self, data):
        return json.dumps(data, default=self.custom_encoder)

    def loads(self, data):
        return json.loads(data, object_hook=self.custom_decoder)
