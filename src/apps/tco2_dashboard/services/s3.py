from ....util import load_s3_data
from . import KeyCacheable, dynamic_caching


class S3(KeyCacheable):
    @dynamic_caching()
    def load(self, slug):
        return load_s3_data(slug)


s3 = S3()
