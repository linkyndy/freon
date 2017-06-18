class BaseBackend(object):
    def get(self, key):
        raise NotImplementedError()

    def set(self, key, value, ttl):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def exists(self, key):
        raise NotImplementedError()

    def get_expired(self):
        raise NotImplementedError()

    def get_by_ttl(self, ttl):
        raise NotImplementedError()
