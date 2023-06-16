from ....util import load_s3_data
from . import KeyCacheable, single_cached_command


class S3(KeyCacheable):
    @single_cached_command()
    def load(self, slug):
        return load_s3_data(slug)


s3 = S3()
