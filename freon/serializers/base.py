class BaseSerializer(object):
    def dumps(self, data):
        raise NotImplementedError()

    def loads(self, data):
        raise NotImplementedError()
