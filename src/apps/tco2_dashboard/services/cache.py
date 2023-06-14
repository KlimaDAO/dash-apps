from flask_caching import Cache
import hashlib
import pickle

# Configure cache
CACHE_TIMEOUT = 86400

cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory",
        "CACHE_DEFAULT_TIMEOUT": CACHE_TIMEOUT,
    },
)


class KeyCacheable():
    def __init__(self):
        self.key: str = None


def dynamic_caching(update_key=False):
    """Decorates a method from a KeyCacheable Object to cache the result using a dynamic key"""

    def inner(func):
        def key_hash(key):
            m = hashlib.sha256()
            m.update(key.encode("utf-8"))
            return m.hexdigest()

        def wrapper(self: KeyCacheable, *args):
            serialized_kwargs = pickle.dumps(args)
            start = f"{self.key}_" if self.key else ""

            # Create a key and a hash for this function call
            key = f"{start}{func.__name__}_{serialized_kwargs}"
            if update_key:
                self.key = key
            hash = key_hash(key)

            # Execute function and cache result
            res = cache.get(hash)
            
            if res is None:
                res = func(self, *args)
                cache.set(hash, res)
                print(f"get no cache {hash} {key}")
            else:
                print(f"get wt cache {hash} {key}")

            # return Result
            return res
        
        return wrapper

    return inner
