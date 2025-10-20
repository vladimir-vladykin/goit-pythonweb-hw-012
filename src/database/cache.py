from redis import Redis

redis = Redis(host="redis", port=6379, db=0)


def get_from_cache(key):
    return redis.get(str(key))


def put_into_cache(key, value):
    redis.set(str(key), value)
    redis.expire(str(key), 3600)

