from importlib import import_module


class Cache(object):
    """
    Connection to a cache backend

    :param backend: Name of backend to connect to. Can be one of ``redis`` or
     ``memory``
    :param serializer: Name of serializer used to serialize/deserialized cached
     values. Can be the name of any module that provides ``dumps()`` and
     ``loads()``
    """

    def __init__(self, backend='redis', serializer='msgpack', default_ttl=3600,
                 **kwargs):
        self.backend = self._load_backend(backend, **kwargs)
        self.serializer = self._load_serializer(serializer)
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

        if not lock.acquire(blocking=False):
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

    def get_or_create(self, key, value, ttl=None):
        existing_value, existing_expired = self.backend.get(key)

        if not existing_expired:
            return existing_value

        result = self.set(key, value, ttl)
        return result if result else None

    def delete(self, key):
        return self.backend.delete(key)

    def exists(self, key):
        return self.backend.exists(key)

    def get_by_ttl(self, ttl):
        return self.backend.get_by_ttl(ttl)

    def _load_backend(self, name, **config):
        module = import_module("freon.backends.%s" % name)
        backend_cls = getattr(module, "%sBackend" % name.capitalize())
        return backend_cls(**config)

    def _load_serializer(self, name):
        return import_module(name)

#
#
# config = {
#     'backend': 'redis',
#     'host': 'localhost',
#     'serializer': 'msgpack'
# }
#
# cache = Cache(backend='redis', serializer='msgpack')
# cache.set('bla', 'dddd', 43)
#
# redis_backend = RedisBackend(host='localhost')
# msgpack_serializer = import_module('msgpack')
# cache = Cache(backend=redis_backend, serializer=msgpack_serializer)
# cache.set('bla', 'dddd', 43)
#
# cache = Cache()
# cache.configure(config)
#
# cache = Cache()
# cache.config.from_dict(config)
#
# cache = Cache.from_config(config)



    # def get_or_set(self, key, value, ttl):
    #     self.get(key)
    #     if no_key:
    #         acquire_lock_no_blocking
    #
    #         if lock:
    #             self.set(key, value, ttl)
    #             release_lock
    #         else:
    #             return_old_data
