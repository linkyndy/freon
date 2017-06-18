local key = KEYS[1]

return redis.call('EXISTS', key)
