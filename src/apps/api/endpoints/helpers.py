import re
import pandas as pd
import math
from flask_restful import reqparse
from flask import request
import dateutil
from werkzeug.exceptions import BadRequest
from src.apps.services import KeyCacheable, DashArgumentException

API_MAJOR_VERSION = "v1"
API_MINOR_VERSION = "0.1"


def subendpoints_help(endpoints):
    """Returns a json response with a list of sub endpoints"""
    match = re.match("(.*/api/v1).*", request.base_url)
    api_url = match.group(1)
    return {
        'api': 'dash-api',
        'version': f"{API_MAJOR_VERSION}.{API_MINOR_VERSION}",
        'endpoints': endpoints,
        'help': f'Use {api_url}/<endpoint>?help for assistance'
    }


def validate_list(valid_values):
    """Returns a function that validates an argument against a list of values"""
    def func(s):
        s = s.lower()
        if s in valid_values:
            return s
        valid_values_without_none = [item for item in valid_values if item]
        raise DashArgumentException(f"Valid values are {', '.join(valid_values_without_none)}")
    return func


help_parser = reqparse.RequestParser()
help_parser.add_argument('help', default="no")


# HELP DECORATOR
def with_help(help_text):
    """Sends a help message if requested to or execute normal command"""
    def Inner(func):
        def wrapper(*func_args, **kwargs):
            args = help_parser.parse_args()
            if args["help"] != "no":
                return {
                    "help": help_text
                }
            return func(*func_args, **kwargs)
        return wrapper
    return Inner

# OUTPUT FORMATTER DECORATOR


MAX_PAGE_SIZE = 2000000
DEFAULT_PAGE_SIZE = 20


def validate_page_size(s):
    """Page size validator -1 is a secret value to get one page containng all results"""
    try:
        s = int(s)
    except ValueError:
        raise DashArgumentException("page_size must be an integer")
    if (s >= 1 and s <= MAX_PAGE_SIZE) or s == -1:
        return s
    raise DashArgumentException(f"page_size must be between 1 and {MAX_PAGE_SIZE}")


output_formatter_parser = reqparse.RequestParser()
output_formatter_parser.add_argument('help', default="no")
output_formatter_parser.add_argument('format', type=validate_list(["json", "csv"]), default="json")
output_formatter_parser.add_argument('page', type=int, default=0)
output_formatter_parser.add_argument('page_size', type=validate_page_size, default=DEFAULT_PAGE_SIZE)
output_formatter_parser.add_argument('sort_by', default=0)
output_formatter_parser.add_argument('sort_order', type=validate_list(["asc", "desc"]), default="asc")


def with_errors_handler(func):
    """Decorator to rethrow DashArgumentExceptions as 400 Bad requests"""
    def wrapper(*func_args, **kwargs):
        try:
            return func(*func_args, **kwargs)
        except DashArgumentException as e:
            raise BadRequest(e.description)
    return wrapper


def with_output_formatter(func):
    def wrapper(*func_args, **kwargs):
        # Execute comamnd
        df: pd.DataFrame = func(*func_args, **kwargs)

        # Resolve value if it is not resolved already
        if isinstance(df, KeyCacheable):
            df = df.resolve()

        # If we have a series to dataframe 
        if isinstance(df, pd.core.series.Series):
            df = df.to_frame()

        # Parse pagination arguments
        args = output_formatter_parser.parse_args()

        # Sort results
        sort_by = args["sort_by"]
        sort_order = args["sort_order"]
        if sort_by:
            if sort_by not in df:
                raise DashArgumentException(f"Invalid sort column '{sort_by}'")
            df = df.sort_values(by=sort_by, ascending=sort_order == "asc")

        # Paginate results
        items_count = df.shape[0]
        page = args["page"]
        page_size = args["page_size"]
        format = args["format"]

        if page_size == -1:
            page_size = items_count

        # Compute info
        pages_count = math.ceil(items_count / page_size)

        # Slice dataframe
        df = df[page_size * page:page_size * (page + 1)]
        # Return result
        if format == "json":
            return {
                "items": df.to_dict('records'),
                "items_count": items_count,
                "current_page": page,
                "pages_count": pages_count
            }
        if format == "csv":
            return df.to_csv()

    return wrapper


OUTPUT_FORMATTER_HELP = (
        f"""page: Page to query
        page_size: Between 1 and {MAX_PAGE_SIZE}
        format: One of 'json' or 'csv'
        sort_by: Column to sort results on
        sort_order: asc or desc
        You can filter dates using '<date_column> gt' and '<date_column> gt'
        """
)


DATES_FILTER_HELP = """You can filter dates using '<date_column>_gt' and '<date_column>_gt'"""


# DATE RANGE Filter
def isotime(s):
    return dateutil.parser.parse(s)


def with_daterange_filter(column):
    """Sends a help message if requested to or execute normal command"""
    daterange_parser = reqparse.RequestParser()
    daterange_parser.add_argument(f'{column}_gt', type=isotime)
    daterange_parser.add_argument(f'{column}_lt', type=isotime)

    def Inner(func):
        def wrapper(*func_args, **kwargs):
            # Execute comamnd
            cacheable = func(*func_args, **kwargs)
            args = daterange_parser.parse_args()
            greater_than = args[f'{column}_gt']
            lower_than = args[f'{column}_lt']
            cacheable.date_range(column, greater_than, lower_than)
            return cacheable

        return wrapper
    return Inner
