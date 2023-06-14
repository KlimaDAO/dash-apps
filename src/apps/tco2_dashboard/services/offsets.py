from .s3 import s3
from . import KeyCacheable, dynamic_caching


class Offsets(KeyCacheable):
    def __init__(self):
        super(Offsets, self).__init__()
        self.filters = {
            "bridge": None,
            "date_range": None
        }

    def bridge(self, bridge):
        """Adds a bridge filter"""
        self.filters["bridge"] = bridge
        return self

    def date_range(self, begin, end):
        """Adds a date range filter"""
        self.filters["date_range"] = {
            "begin": begin,
            "end": end,
        }
        return self

    @dynamic_caching(True)
    def dataframe_cached(self, filters=None):
        """Returns a cached version of the filtered dataframe"""
        df = s3.load("polygon_bridged_offsets")
        bridge = filters["bridge"]
        date_range = filters["date_range"]

        # Bridge filtering
        if bridge:
            df = df[df["Bridge"] == bridge].reset_index()

        # Date range filtering
        if date_range:
            end = date_range["end"]
            begin = date_range["begin"]
            if type(end) != int:
                end = end.timestamp()
            if type(begin) != int:
                begin = begin.timestamp()
            df = df[
                (df["Date"] <= end)
                & (df["Date"] > begin)
            ]
        return df

    @property
    def dataframe(self):
        """Returns a cached version of the filtered dataframe"""
        return self.dataframe_cached(self.filters)

    @dynamic_caching()
    def sum(self, column):
        return self.dataframe[column].sum()



        
