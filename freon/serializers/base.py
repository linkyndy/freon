class BaseSerializer(object):
    def __init__(self, custom_encoder=None, custom_decoder=None):
        self.custom_encoder = custom_encoder
        self.custom_decoder = custom_decoder

    def dumps(self, data):
        raise NotImplementedError()

    def loads(self, data):
        raise NotImplementedError()
