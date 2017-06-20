from importlib import import_module


class Cache(object):
    """
    Connection to a cache backend

    :param backend: Name of backend to connect to. Can be one of ``redis`` or
     ``memory``
    :param serializer: Name of serializer used to serialize/deserialize cached
     values. Can be one of ``msgpack``, ``pickle`` or ``json``
    """

    def __init__(self, backend='redis', serializer='msgpack', default_ttl=3600,
                 custom_encoder=None, custom_decoder=None, **kwargs):
        self.backend = self._load_backend(backend, **kwargs)
        self.serializer = self._load_serializer(serializer, custom_encoder, custom_decoder)
        self.default_ttl = default_ttl

    # TODO: configure if don't want to be constructivist and always return what
    # there is, even if expired
    def get(self, key):
        value, _ = self.backend.get(key)

        if value is None:
            return None

        return self.serializer.loads(value)

    def set(self, key, value, ttl=None):
        lock = self.backend.get_lock(key)

        if not lock.acquire(False):
            return None

        try:
            if callable(value):
                value = value()
            if not ttl:
                ttl = self.default_ttl

            result = self.backend.set(key, self.serializer.dumps(value), ttl)
            return value if result else None
        finally:
            lock.release()

    def get_or_set(self, key, new_value, ttl=None):
        value, expired = self.backend.get(key)

        if value is None or expired:
            result = self.set(key, new_value, ttl)
            return result if result else None

        return self.serializer.loads(value)

    def delete(self, key):
        return self.backend.delete(key)

    def exists(self, key):
        return self.backend.exists(key)

    def get_expired(self):
        return self.backend.get_expired()

    def get_by_ttl(self, ttl):
        return self.backend.get_by_ttl(ttl)

    def _load_backend(self, name, **config):
        module = import_module("freon.backends.%s" % name)
        backend_cls = getattr(module, "%sBackend" % name.capitalize())
        return backend_cls(**config)

    def _load_serializer(self, name, *config):
        module = import_module("freon.serializers.%s" % name)
        serializer_cls = getattr(module, "%sSerializer" % name.capitalize())
        return serializer_cls(*config)
