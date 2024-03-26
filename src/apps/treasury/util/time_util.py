from datetime import datetime
import calendar


def get_date_timestamp_string(timestamp):
    '''
    Parse and return provided datetime timestamp into date timestamp string
    Example: 1655462491 (17 June 2022 10:41:31) would parse to 1655424000 (17 June 2022 00:00:00)
    and return `2022-06-17 00:00:00` as string
    '''
    date_from_timestamp = datetime.fromtimestamp(timestamp)
    date_string = date_from_timestamp.strftime("%d/%m/%Y")
    date = datetime.strptime(date_string, "%d/%m/%Y")
    current_date_timestamp = round(calendar.timegm(date.timetuple()))

    return str(datetime.fromtimestamp(current_date_timestamp))
