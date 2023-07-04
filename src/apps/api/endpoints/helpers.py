import pandas as pd
import math
from flask_restful import reqparse
import dateutil

help_parser = reqparse.RequestParser()
help_parser.add_argument('help', default="no")


# HELP DECORATOR

def with_help(help_text):
    """Sends a help message if requested to or execute normal command"""
    def Inner(func):
        def wrapper(*args, **kwargs):
            args = help_parser.parse_args()
            if args["help"] != "no":
                return {
                    "help": help_text
                }
            return func(*args, **kwargs)
        return wrapper
    return Inner

# PAGINATION DECORATOR


MAX_PAGE_SIZE = 20


def validate_page_size(s):
    """Page size validator"""
    try:
        s = int(s)
    except ValueError:
        raise Exception("page_size must be an integer")
    if s >= 1 and s <= MAX_PAGE_SIZE:
        return s
    raise Exception(f"page_size must be between 1 and {MAX_PAGE_SIZE}")


pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('help', default="no")
pagination_parser.add_argument('page', type=int, default=0)
pagination_parser.add_argument('page_size', type=validate_page_size, default=MAX_PAGE_SIZE)


def with_pagination_filter(func):
    def wrapper(*func_args, **kwargs):
        # Execute comamnd
        df: pd.DataFrame = func(*func_args, **kwargs)

        # Resolve result if necessary
        if type(df) != pd.DataFrame:
            df = df.resolve()

        # Parse pagination arguments
        args = pagination_parser.parse_args()
        page = args["page"]
        page_size = args["page_size"]

        # Compute info
        items_count = df.shape[0]
        pages_count = math.ceil(items_count / page_size)

        # Slice dataframe
        df = df[page_size * page:page_size * (page + 1)]

        # Return result
        return {
            "items": df.to_dict('records'),
            "items_count": items_count,
            "current_page": page,
            "pages_count": pages_count
        }
    return wrapper


PAGINATION_HELP = (
        f"""page: page to query
        page_size: between 1 and {MAX_PAGE_SIZE}
        """
)


# DATE RANGE Filter
def isotime(s):
    return dateutil.parser.parse(s)


def with_daterange_filter(slug, column):
    """Sends a help message if requested to or execute normal command"""
    daterange_parser = reqparse.RequestParser()
    daterange_parser.add_argument(f'{slug}_gt', type=isotime)
    daterange_parser.add_argument(f'{slug}_lt', type=isotime)

    def Inner(func):
        def wrapper(*func_args, **kwargs):
            # Execute comamnd
            cacheable = func(*func_args, **kwargs)
            args = daterange_parser.parse_args()
            greater_than = args[f'{slug}_gt']
            lower_than = args[f'{slug}_lt']
            cacheable.date_range(column, greater_than, lower_than)
            return cacheable

        return wrapper
    return Inner
