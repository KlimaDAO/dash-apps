from . import S3
from . import KeyCacheable, single_cached_command


class Tokens(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        self.df = S3().load("tokens_data")
        super(Tokens, self).__init__(commands)

    def get_dict(self):
        return (
            self.df
            .set_index("Name")
            .transpose()
            .to_dict(orient='dict')
        )

    @single_cached_command()
    def all(self):
        return self.get_dict()

    @single_cached_command()
    def get(self, pool) -> str:
        return self.get_dict()[pool]
