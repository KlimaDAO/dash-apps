import pycountry
from . import KeyCacheable, single_cached_command, services_short_cache


class Countries(KeyCacheable):
    def __init__(self, commands=[]):
        super(Countries, self).__init__(commands, services_short_cache)

    @single_cached_command()
    def get_country(self, country):
        """Returns a pycountry country object"""
        if country == "nan" or country is None:
            return "None"
        return pycountry.countries.search_fuzzy(country)[0].alpha_3
