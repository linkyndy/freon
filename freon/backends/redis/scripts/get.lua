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
