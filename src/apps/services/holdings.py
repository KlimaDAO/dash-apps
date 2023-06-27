from . import S3, KeyCacheable


class Holdings(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        self.df = S3().load("raw_offsets_holders_data")
        super(Holdings, self).__init__(commands)

    def get(self):
        return self.df
