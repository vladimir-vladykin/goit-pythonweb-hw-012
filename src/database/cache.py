from redis import Redis
from abc import ABC, abstractmethod


class Cache(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put(self, key, value):
        pass


class RedisCache(Cache):

    def __init__(self):
        self.redis = Redis(host="redis", port=6379, db=0)

    def get(self, key):
        return self.redis.get(str(key))

    def put(self, key, value):
        self.redis.set(str(key), value)
        self.redis.expire(str(key), 3600)


cache: Cache = None


def get_cache() -> Cache:
    global cache
    if cache is None:
        cache = RedisCache()

    return cache
