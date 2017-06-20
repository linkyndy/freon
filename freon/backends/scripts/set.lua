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
