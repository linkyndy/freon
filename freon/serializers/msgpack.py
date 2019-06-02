from __future__ import absolute_import
import msgpack

from freon.serializers.base import BaseSerializer


class MsgpackSerializer(BaseSerializer):
    def dumps(self, data):
        return msgpack.dumps(data, use_bin_type=True, default=self.custom_encoder)

    def loads(self, data):
        return msgpack.loads(data, raw=False, object_hook=self.custom_decoder)
