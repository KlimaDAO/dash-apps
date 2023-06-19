import pycountry
from . import KeyCacheable, single_cached_command


class Countries(KeyCacheable):
    def __init__(self, commands=[]):
        super(Countries, self).__init__(commands)

    @single_cached_command()
    def get_country(self, country):
        """Returns a pycountry coutnry object"""
        if country != "nan":
            return pycountry.countries.search_fuzzy(country)[0].alpha_3
        return country
