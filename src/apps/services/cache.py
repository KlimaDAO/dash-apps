from flask_caching import Cache
import hashlib
import pickle
import copy
from ...util import getenv # noqa

# Configure cache
LAYOUT_CACHE_TIMEOUT = int(getenv("DASH_LAYOUT_CACHE_TIMEOUT", 86400))
SERVICES_CACHE_TIMEOUT = int(getenv("DASH_SERVICES_CACHE_TIMEOUT", 86400))

layout_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/layout",
        "CACHE_DEFAULT_TIMEOUT": LAYOUT_CACHE_TIMEOUT,
    },
)
services_slow_cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory/services",
        "CACHE_DEFAULT_TIMEOUT": SERVICES_CACHE_TIMEOUT,
    },
)
services_fast_cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
    },
)


def key_hash(key: str):
    """Hashes a string"""
    m = hashlib.sha256()
    m.update(key.encode("utf-8"))
    return m.hexdigest()


class KeyCacheable():
    """A base class that enabe extending classes to use the cache decorators"""
    def __init__(self, commands=[], cache=services_slow_cache):
        self.cache_key: str = None
        self.cache = cache
        self.commands = commands.copy()
        if commands:
            self.cache_key = commands[-1]["key"]

    def copy(self):
        return self.__class__(copy.deepcopy(self.commands))

    def add_command(self, is_final_command, takes_input, func, *args):
        """Adds a command to the command list

        Arguments:
        is_final_command: Is the function should return directly the result
        takes_input: Should we pass an input to the function
        func: The function to be executed
        args: The function's arguments
        """
        serialized_kwargs = pickle.dumps(args)
        start = f"{self.cache_key}_" if self.cache_key else ""
        self.cache_key = f"{start}{func.__name__}_{serialized_kwargs}"
        hash = key_hash(self.cache_key)

        self.commands.append({
            "func": func,
            "args": args,
            "hash": hash,
            "key": self.cache_key,
            "is_final_command": is_final_command,
            "takes_input": takes_input
        })

    def get_most_recent_cached_result(self):
        """ Returns the index of the latest command with a cached result """
        idx = len(self.commands) - 1
        res = None
        while idx >= 0:
            command = self.commands[idx]
            res = self.cache.get(command["hash"])
            if res is not None:
                break
            idx = idx - 1

        return res, idx

    def resolve(self):
        """Resolves the command list"""

        # Get the most precise cached command
        res, idx = self.get_most_recent_cached_result()

        # Resolve the rest without cache
        while idx + 1 < len(self.commands):
            idx = idx + 1
            command = self.commands[idx]

            if command["takes_input"]:
                res = command["func"](self, res, *command["args"])
            else:
                res = command["func"](self, *command["args"])

            # Cache the results
            self.cache.set(command["hash"], res)

        return res


def cached_command(is_final_command, takes_input):
    """Decorates a class method to put it in a command list"""
    def inner(func):
        def wrapper(self: KeyCacheable, *args):
            self.add_command(is_final_command, takes_input,  func, *args)
            if not is_final_command:
                return self
            else:
                return self.resolve()
        return wrapper
    return inner


def final_cached_command():
    """Decorates a method to be cached. The method returns the result immediately"""
    return cached_command(is_final_command=True, takes_input=True)


def chained_cached_command():
    """Decorates a method to be cached. The method returns the class instance"""
    return cached_command(is_final_command=False, takes_input=True)


def single_cached_command():
    """Decorates a method to be cached. The method returns the result immediately and does not take inputs"""
    return cached_command(is_final_command=True, takes_input=False)
