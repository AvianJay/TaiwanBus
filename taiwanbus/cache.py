import time

CACHE_TIME = 10  # seconds
cache = []


def get_cache(key):
    for item in cache:
        if item['key'] == key:
            if time.time() - item['timestamp'] < item['expire_time']:
                return item['value']
            else:
                cache.remove(item)  # Remove expired item
                break
    return None


def set_cache(key, value, expire_time=CACHE_TIME) -> None:
    # Remove existing item if it exists
    for item in cache:
        if item['key'] == key:
            cache.remove(item)
            break
    # Add new item to cache
    cache.append(
        {
            'key': key,
            'value': value,
            'timestamp': time.time(),
            'expire_time': expire_time
        }
    )
    # Ensure cache size does not exceed 100 items
    if len(cache) > 100:
        cache.pop(0)  # Remove the oldest item
