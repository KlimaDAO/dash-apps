from flask import jsonify
from flask_restful import Api
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
import traceback
import pandas as pd
from datetime import date, datetime


# See https://stackoverflow.com/questions/41149409/flask-restful-custom-error-handling
class DashApi(Api):
    """This class overrides 'handle_error' method of 'Api' class ,
    to extend global exception handing functionality of 'flask-restful'.
    """
    def handle_errors(self, err):
        """It helps preventing writing unnecessary
        try/except block though out the application
        """
        # Handle HTTPExceptions
        traceback.print_exc()
        if isinstance(err, HTTPException):
            return jsonify({
                    'message': getattr(
                        err, 'description', HTTP_STATUS_CODES.get(err.code, '')
                    )
                }), err.code

        # If msg attribute is not set,
        # consider it as Python core exception and
        # hide sensitive error info from end user
        if not getattr(err, 'message', None):
            return jsonify({
                'message': 'Server has encountered some error'
                }), 500
        # Handle application specific custom exceptions
        return jsonify(**err.kwargs), err.http_status_code


# Fixes for json serialisation of date and datetime
def json_default_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, (pd.Period)):
        return obj.to_timestamp().to_pydatetime()
    raise Exception("Type %s not serializable" % type(obj))