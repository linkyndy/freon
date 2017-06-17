from __future__ import absolute_import
from redis import StrictRedis

from freon.backends.base import BaseBackend


class RedisBackend(BaseBackend):
    def __init__(self, host='localhost', port=6379, db=0, password=None, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.config = kwargs
        self.zset_key = 'freon:ttls'
        self._connection = None
        self._register_scripts()

    @property
    def connection(self):
        if not self._connection:
            self._connection = StrictRedis(host=self.host,
                                           port=self.port,
                                           db=self.db,
                                           password=self.password,
                                           **self.config)
        return self._connection

    def get_lock(self, name):
        return self.connection.lock("%s_lock" % name, timeout=1)

    def get(self, key):
        return self._lua_get(keys=[key, self.zset_key])

        # with self.connection.pipeline() as pipe:
        #     value = pipe.get(key)
        #     expire_at = pipe.zscore('av_cache_ttls', key)
        # return value, expire_at

    def set(self, key, value, ttl):
        return self._lua_set(keys=[key, self.zset_key], args=[value, ttl])

        # with self.connection.pipeline() as pipe:
        #     pipe.set(key, value)
        #     time = pipe.time()[0]
        #     time + expire_in
        #     pipe.zadd('av_cache_ttls', expire_at, key)
        #     # pipe.execute()

    def delete(self, key):
        return self._lua_delete(keys=[key, self.zset_key])

        # with self.connection.pipeline() as pipe:
        #     pipe.delete(key)
        #     pipe.zrem('av_cache_ttls', expire_at, key)

    def exists(self, key):
        return self._lua_exists(keys=[key])

        # return self.connection.exists(key)

    def get_by_ttl(self, ttl):
        return self._lua_get_by_ttl(ttl)

    def _register_scripts(self):
        self._lua_get = self.connection.register_script(LUA_GET)
        self._lua_set = self.connection.register_script(LUA_SET)
        self._lua_delete = self.connection.register_script(LUA_DELETE)
        self._lua_exists = self.connection.register_script(LUA_EXISTS)
        self._lua_get_by_ttl = self.connection.register_script(LUA_GET_BY_TTL)

LUA_GET = """
    redis.replicate_commands()

    local key = KEYS[1]
    local zset = KEYS[2]

    local time = redis.call('TIME')[1]

    local value = redis.call('GET', key)

    if value then
        local expires_at = redis.call('ZSCORE', zset, key)
        local is_expired = expires_at < time
        return {value, is_expired}
    else
        return {false, true}
    end
"""

LUA_SET = """
    redis.replicate_commands()

    local key = KEYS[1]
    local zset = KEYS[2]
    local value = ARGV[1]
    local ttl = tonumber(ARGV[2])

    local time = redis.call('TIME')[1]
    local expires_at = time + ttl

    redis.call('SET', key, value)
    redis.call('ZADD', zset, expires_at, key)
    return true
"""

LUA_DELETE = """
    local key = KEYS[1]
    local zset = KEYS[2]

    redis.call('DEL', key)
    redis.call('ZREM', zset, key)
"""

LUA_EXISTS = """
    local key = KEYS[1]

    return redis.call('EXISTS', key)
"""

LUA_GET_BY_TTL = """
    redis.replicate_commands()

    local zset = KEYS[1]
    local ttl = tonumber(ARGV[1])
    local time = redis.call('TIME')[1]

    return redis.call('ZRANGEBYSCORE', zset, 0, time + ttl)
"""
