from flask_caching import Cache
import hashlib
import pickle
import copy
from ....util import debug

# Configure cache
CACHE_TIMEOUT = 10

cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "/tmp/cache-directory",
        "CACHE_DEFAULT_TIMEOUT": CACHE_TIMEOUT,
    },
)


def key_hash(key: str):
    """Hashes a string"""
    m = hashlib.sha256()
    m.update(key.encode("utf-8"))
    return m.hexdigest()


class KeyCacheable():
    """A base class that enabe extending classes to use the cache decorators"""
    def __init__(self, commands=[]):
        self.cache_key: str = None
        self.commands = commands.copy()
        if commands:
            self.cache_key = commands[-1]["key"]

    def copy(self):
        return self.__class__(copy.deepcopy(self.commands))

    def add_command(self, is_single_command, takes_input, func, *args):
        """Adds a command to the command list

        Arguments:
        is_single_command: Is the function should return directly the result
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
            "is_single_command": is_single_command,
            "takes_input": takes_input
        })

    def get_most_recent_cached_command_index(self):
        """ Returns the index of the latest command with a cached result """
        idx = len(self.commands) - 1
        while idx >= 0:
            command = self.commands[idx]
            res = cache.get(command["hash"])
            if res is not None:
                return idx
            idx = idx - 1

        return idx

    def get(self):
        """Resolves the command list"""

        # Get the most precise cached command
        idx = self.get_most_recent_cached_command_index()
        res = None
        if idx >= 0:
            command = self.commands[idx]
            res = cache.get(command["hash"])
            debug(f"get wt cache | {command['key']}\n")

        # Resolve the rest without cache
        while idx + 1 < len(self.commands):
            idx = idx + 1
            command = self.commands[idx]
            debug(f"get no cache | {command['key']}\n")
            if command["takes_input"]:
                res = command["func"](self, res, *command["args"])
            else:
                res = command["func"](self, *command["args"])

            # Cache the results
            cache.set(command["hash"], res)

        return res


def cached_command(is_final_command, takes_input):
    """Decorates a class method to put it in a command list"""
    def inner(func):
        def wrapper(self: KeyCacheable, *args):
            self.add_command(is_final_command, takes_input,  func, *args)
            if not is_final_command:
                return self
            else:
                return self.get()
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
