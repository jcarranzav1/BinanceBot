from datetime import datetime
from datetime import date, timedelta
import time


def date_to_string(date):  # Convierte las fechas a atrings
    return date.strftime('%Y-%m-%d %H:%M:%S')


def string_to_date(string):  # Convierte los string en fechas
    return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


# Covierte los tipos de fechas unix en fechas datetime.
def unix_to_date(unix):
    date = time.gmtime(unix / 1000)
    date = time.strftime('%Y-%m-%d %H:%M:%S', date)
    date = string_to_date(date)
    return date
