from ...util import load_s3_data
from . import KeyCacheable, single_cached_command, services_long_cache


class S3(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[], cache=services_long_cache):
        super(S3, self).__init__(commands, cache)

    @single_cached_command()
    def load(self, slug):
        return load_s3_data(slug)
