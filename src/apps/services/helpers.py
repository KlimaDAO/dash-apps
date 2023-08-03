ALL_BRIDGES = ["toucan", "c3", "moss"]
ALL_TOKENS = ["ubo", "nbo", "mco2", "nct", "bct"]


class DashArgumentException(Exception):
    code = 400

    def __init__(self, description):
        self.description = description


def status_date_column(status):
    if status == "issued":
        return "issuance_date"
    elif status == "bridged":
        return "bridged_date"
    elif status == "retired":
        return "retirement_date"
    elif status == "redeemed":
        return "redeemed_date"
    elif status == "deposited":
        return "deposited_date"
    else:
        raise DashArgumentException("Unknown status")
