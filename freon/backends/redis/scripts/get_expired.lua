redis.replicate_commands()

local zset = KEYS[1]
local time = redis.call('TIME')[1]

return redis.call('ZRANGEBYSCORE', zset, 0, time)
