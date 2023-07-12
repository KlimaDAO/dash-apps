from werkzeug.exceptions import HTTPException


ALL_BRIDGES = ["toucan", "c3", "moss"]


class DashArgumentException(HTTPException):
    code = 400
