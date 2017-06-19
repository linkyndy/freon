local key = KEYS[1]
local zset = KEYS[2]

redis.call('DEL', key)
redis.call('ZREM', zset, key)
return true
