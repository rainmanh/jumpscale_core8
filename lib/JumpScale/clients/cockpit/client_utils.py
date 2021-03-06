import datetime
import time


def build_query_string(query_params=None):
    """
    build query parameter
    input  `query_params` : dictionary
    output string with format `?key=val&key2=val2`
    """
    if query_params is None:
        return ""

    qs = "?"
    for key, elem in query_params.items():
        qs += key + "=" + str(elem) + "&"

    return qs[:-1]


def generate_rfc3339(d, local_tz=True):
    """
    generate rfc3339 time format
    input :
    d = date type
    local_tz = use local time zone if true,
    otherwise mark as utc

    output :
    rfc3339 string date format. ex : `2008-04-02T20:00:00+07:00`
    """
    try:
        if local_tz:
            d = datetime.datetime.fromtimestamp(d)
        else:
            d = datetime.datetime.utcfromtimestamp(d)
    except TypeError:
        pass

    if not isinstance(d, datetime.date):
        raise TypeError('Not timestamp or date object. Got %r.' % type(d))

    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(*d.timetuple()[:3])

    return ('%04d-%02d-%02dT%02d:%02d:%02d%s' %
            (d.year, d.month, d.day, d.hour, d.minute, d.second,
             _generate_timezone(d, local_tz)))


def _calculate_offset(date, local_tz):
    """
    input :
    date : date type
    local_tz : if true, use system timezone, otherwise return 0

    return the date of UTC offset.
    If date does not have any timezone info, we use local timezone,
    otherwise return 0
    """
    if local_tz:
        # handle year before 1970 most sytem there is no timezone information
        # before 1970.
        if date.year < 1970:
            # Use 1972 because 1970 doesn't have a leap day
            t = time.mktime(date.replace(year=1972).timetuple)
        else:
            t = time.mktime(date.timetuple())

        # handle daylightsaving, if daylightsaving use altzone, otherwise use
        # timezone
        if time.localtime(t).tm_isdst:
            return -time.altzone
        else:
            return -time.timezone
    else:
        return 0


def _generate_timezone(date, local_tz):
    """
    input :
    date : date type
    local_tz : bool

    offset generated from _calculate_offset
    offset in seconds
    offset = 0 -> +00:00
    offset = 1800 -> +00:30
    offset = -3600 -> -01:00
    """
    offset = _calculate_offset(date, local_tz)

    hour = abs(offset) // 3600
    minute = abs(offset) % 3600 // 60

    if offset < 0:
        return '%c%02d:%02d' % ("-", hour, minute)
    else:
        return '%c%02d:%02d' % ("+", hour, minute)
