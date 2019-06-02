from importlib import import_module


class Cache(object):
    """
    Connection to a cache backend

    :param backend: (optional) Name of backend to connect to. Can be one of ``redis`` or ``memory``. Defaults to ``memory``.
    :type backend: string
    :param serializer: (optional) Name of serializer used to serialize/deserialize cached values. Can be one of ``msgpack``, ``pickle`` or ``json``. Defaults to ``json``.
    :type serializer: string
    :param default_ttl: (optional) Default TTL applied to items that don't have one associated. Value is expressed in seconds. Defaults to ``3600``.
    :type default_ttl: integer
    :param custom_encoder: (optional) Custom encoder to extend the serializer's default behaviour.
    :type custom_encoder: None or callable
    :param custom_decoder: (optional) Custom decoder to extend the serializer's default behaviour.
    :type custom_decoder: None or callable
    :param **kwargs: (optional) Extra arguments, passed to the selected backend.

    Usage::

      >>> from freon.cache import Cache
      >>> cache = Cache()
      >>> cache.get('foobar')
      None
    """

    def __init__(self, backend='memory', serializer='json', default_ttl=3600,
                 custom_encoder=None, custom_decoder=None, **kwargs):

        self.backend = self._load_backend(backend, **kwargs)
        self.serializer = self._load_serializer(serializer, custom_encoder, custom_decoder)
        self.default_ttl = default_ttl

    # TODO: configure if don't want to be constructivist and always return what
    # there is, even if expired
    def get(self, key):
        """
        Retrieves a cached entry by given key.

        If the key doesn't exist, ``None`` is returned. If the key exists but
        is expired, the cached entry is still returned.

        :param key: Key of cached entry to be retrieved
        :type key: string
        :return: cached object or ``None``
        """

        value, _ = self.backend.get(key)

        if value is None:
            return None

        return self.serializer.loads(value)

    def set(self, key, value, ttl=None):
        """
        Caches an entry by key and by TTL.

        Value can be a callable, in which case it is executed before caching it.
        This is particularly useful to defer creation of the entry to be cached
        as much as possible (or maybe not even create it, if another thread
        already does it).

        TTL can be a callable, in which case it is executed before caching the
        entry. It must accept an argument in this case, which will be passed the
        value of the entry to be cached. This is particularly useful to defer
        the computation of the TTL until it is really necessary, or to depend on
        a deferred creation of the value (think of dynamically assigning a TTL
        based on an attribute of the value).

        This method avoids the dog-pile effect by using a lock. If some other
        thread is already involved in caching the entry, it simply returns ``None``.

        :param key: Key under which the entry will be cached
        :type key: string
        :param value: The actual entry to be cached
        :type value: string or callable
        :param ttl: (optional) TTL to be associated with the cached entry. Defaults to ``self.default_ttl``
        :type ttl: integer, callable or ``None``
        :return: cached object or ``None``
        """

        lock = self.backend.get_lock(key)

        if not lock.acquire(False):
            return None

        try:
            if callable(value):
                value = value()
            if callable(ttl):
                ttl = ttl(value)
            elif not ttl:
                ttl = self.default_ttl

            result = self.backend.set(key, self.serializer.dumps(value), ttl)
            return value if result else None
        finally:
            lock.release()

    def get_or_set(self, key, new_value, ttl=None):
        """
        Tries to retrieve a cached entry by key. If the value does not exist,
        it caches the entry by key and TTL.

        :param key: Key of cached entry to be retrieved or under which the entry will be cached
        :type key: string
        :param new_value: The actual entry to be cached
        :type new_value: string or callable
        :param ttl: (optional) TTL to be associated with the cached entry. Defaults to ``self.default_ttl``
        :type ttl: integer, callable or ``None``
        :return: cached object, newly cached object or ``None``
        """

        value, expired = self.backend.get(key)

        if value is None or expired:
            result = self.set(key, new_value, ttl)
            return result if result else value

        return self.serializer.loads(value)

    def delete(self, key):
        """
        Deletes a cached entry by key.

        :param key: Key of cached entry to be deleted
        :type key: string
        :return: bool
        """

        return self.backend.delete(key)

    def exists(self, key):
        """
        Checks whether a cached entry exists by key.

        :param key: Key of cached entry to be checked
        :type key: string
        :return: bool
        """

        return self.backend.exists(key)

    def get_expired(self):
        """
        Returns a list of expired keys.

        :return: list of strings
        """

        return self.backend.get_expired()

    def get_by_ttl(self, ttl):
        """
        Returns a list of keys that will expire within the specified threshold.

        :param ttl: Number of seconds from the current time when retrieved keys will expire
        :type ttl: integer
        :return: list of strings
        """

        return self.backend.get_by_ttl(ttl)

    def _load_backend(self, name, **config):
        module = import_module("freon.backends.%s" % name)
        backend_cls = getattr(module, "%sBackend" % name.capitalize())
        return backend_cls(**config)

    def _load_serializer(self, name, *config):
        module = import_module("freon.serializers.%s" % name)
        serializer_cls = getattr(module, "%sSerializer" % name.capitalize())
        return serializer_cls(*config)
