from flask import jsonify
from flask_restful import Api
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
import traceback


# See https://stackoverflow.com/questions/41149409/flask-restful-custom-error-handling
class DashApi(Api):
    """This class overrides 'handle_error' method of 'Api' class ,
    to extend global exception handing functionality of 'flask-restful'.
    """
    def handle_error(self, err):
        """It helps preventing writing unnecessary
        try/except block though out the application
        """
        # Handle HTTPExceptions
        if isinstance(err, HTTPException):
            return jsonify({
                    'message': getattr(
                        err, 'description', HTTP_STATUS_CODES.get(err.code, '')
                    )
                }), err.code
        else:
            traceback.print_exc()

        # If msg attribute is not set,
        # consider it as Python core exception and
        # hide sensitive error info from end user
        if not getattr(err, 'message', None):
            return jsonify({
                'message': 'Server has encountered some error'
                }), 500
        # Handle application specific custom exceptions
        return jsonify(**err.kwargs), err.http_status_code
