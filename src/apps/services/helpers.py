ALL_BRIDGES = ["toucan", "c3", "moss"]
ALL_TOKENS = ["ubo", "nbo", "mco2", "nct", "bct"]


class DashArgumentException(Exception):
    code = 400

    def __init__(self, description):
        self.description = description
