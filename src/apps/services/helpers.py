ALL_BRIDGES = ["toucan", "c3", "moss"]
ALL_TOKENS = ["ubo", "nbo", "mco2", "nct", "bct"]
STATUS_TO_DATE_COLUMN_MATRIX = {
    "issued": "issuance_date",
    "bridged": "bridged_date",
    "deposited": "deposited_date",
    "redeemed": "redeemed_date",
    "retired": "retirement_date"
}


class DashArgumentException(Exception):
    code = 400

    def __init__(self, description):
        self.description = description
