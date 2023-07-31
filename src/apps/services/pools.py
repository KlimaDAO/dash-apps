from . import Offsets, KeyCacheable, DashArgumentException, chained_cached_command, final_cached_command


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
        bridge = bridge.lower()
        if bridge == "toucan":
            pool_labels = ["BCT", "NCT"]
        elif bridge == "c3":
            pool_labels = ["UBO", "NBO"]
        else:
            raise DashArgumentException("Unknown bridge")
        values = [Offsets().filter(bridge, pool, "bridged").sum("Quantity") for pool in pool_labels]

        pool_labels = pool_labels + ["not_pooled"]
        not_pool_qty = Offsets().filter(bridge, "all", "bridged").sum("Quantity") - sum(values)
        values = values + [not_pool_qty]

        return dict(zip(pool_labels, values))
