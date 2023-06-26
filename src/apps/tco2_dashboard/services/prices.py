from . import S3
from . import KeyCacheable, single_cached_command


class Prices(KeyCacheable):
    """Service for carbon metrics"""
    def __init__(self, commands=[]):
        self.df = S3().load("raw_assets_prices")
        super(Prices, self).__init__(commands)

    @single_cached_command()
    def token(self, token):
        col_name = f"{token}_Price"
        a = self.df[col_name].isna()
        return self.df[~a].rename(columns={
            f"{token}_Price": "Price"
        })
