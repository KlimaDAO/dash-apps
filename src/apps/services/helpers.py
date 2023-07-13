ALL_BRIDGES = ["toucan", "c3", "moss"]


class DashArgumentException(Exception):
    code = 400

    def __init__(self, description):
        self.description = description
