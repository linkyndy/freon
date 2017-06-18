redis.replicate_commands()

local zset = KEYS[1]
local ttl = tonumber(ARGV[1])
local time = redis.call('TIME')[1]

return redis.call('ZRANGEBYSCORE', zset, time, time + ttl)
