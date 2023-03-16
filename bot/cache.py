import time
from collections import OrderedDict


class SimpleTTLCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: str) -> str | None:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        value, expire_at = self.cache[key]
        if expire_at < time.time():
            self.cache.pop(key)
            return None
        return value

    def put(self, key: str, value: str, ttl: int) -> None:
        self.cache[key] = (value, time.time() + ttl)
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
