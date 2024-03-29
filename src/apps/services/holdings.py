from . import S3, KeyCacheable


class Holdings(KeyCacheable):
    """Service for holdings"""
    def __init__(self, commands=[]):
        self.df = S3().load("offsets_holders_data")
        super(Holdings, self).__init__(commands)

    def get(self):
        return self.df
