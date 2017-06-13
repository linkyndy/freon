from importlib import import_module
import time


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

        if value:
            return self.serializer.loads(value)
        return value

    def set(self, key, value_or_fn, ttl=None, return_val=False):
        lock = self.backend.get_lock(key)

        if not lock.acquire(blocking=False):
            return False

        try:
            value = value_or_fn() if callable(value_or_fn) else value_or_fn
            value = self.serializer.dumps(value)
            ttl = ttl or self.default_ttl
            return self.backend.set(key, value, ttl)
        finally:
            lock.release()

    def create(self, key, value_or_fn, ttl=None):
        if self.set(key, value_or_fn, ttl):
            return value_or_fn
        else:
            return None

    def get_or_create(self, key, value_or_fn, ttl=None):
        existing_value, existing_expired = self.backend.get(key)

        if existing_expired:
            if self.set(key, value, ttl):
                return value

        return existing_value

    def delete(self, key):
        return self.backend.delete(key)

    def exists(self, key):
        return self.backend.exists(key)

    def get_by_ttl(self, ttl):
        return self.backend.get_by_ttl(ttl)

    __getitem__ = get

    def __setitem__(self, key, value):
        return self.set(key, *value)

    __delitem__ = delete

    __contains__ = exists

    def _load_backend(self, name, **config):
        module = import_module('freon.backends')
        backend_cls = getattr(module, name.capitalize())
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
