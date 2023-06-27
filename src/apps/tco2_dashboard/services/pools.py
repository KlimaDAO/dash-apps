from . import Offsets
from . import KeyCacheable, chained_cached_command, final_cached_command


class Pools(KeyCacheable):
    """Service for offsets"""
    def __init__(self, commands=[]):
        super(Pools, self).__init__(commands)

    @chained_cached_command()
    def filter(self, _res, bridge) -> str:
        return bridge

    @final_cached_command()
    def quantities(self, bridge) -> dict:
        """Returns current pool quantities"""
        if bridge == "Toucan":
            pool_labels = ["BCT", "NCT"]
        elif bridge == "C3":
            pool_labels = ["UBO", "NBO"]
        else:
            raise Exception("Unknown bridge")
        values = [Offsets().filter(bridge, pool, "bridged").sum("Quantity") for pool in pool_labels]

        pool_labels = pool_labels + ["Not Pooled"]
        not_pool_qty = Offsets().filter(bridge, "all", "bridged").sum("Quantity") - sum(values)
        values = values + [not_pool_qty]

        return dict(zip(pool_labels, values))
