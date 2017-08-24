"""
Scraps important semester dates from SVSU registrars calendar webpage
"""
from warnings import warn
from datetime import datetime, timedelta
import requests
import bs4
#import unicodedata
from unidecode import unidecode
from dateutil.relativedelta import relativedelta
from daterangeparser import parse

CAL_BASE = "http://www.svsu.edu/officeoftheregistrar/calendarimportantdates/importantdates/"
FALL_WINTER_URL = CAL_BASE + "fallwinter/"
SPRING_SUMMER_URL = CAL_BASE + "springsummer/"

def extract_table_parts(page):
    """Extract head and body from the calendar table on the given page."""
    # Find the calendar table
    tables = page.select("table")
    if len(tables) == 0:
        raise RuntimeError("There are no tables on this page.")
    if len(tables) > 1:
        warn("There are more tables on the page.  I will use the first one.")
    cal_table = tables[0] # It seems to be the only table on the page
    headlist = cal_table.find_all("thead")
    if len(headlist) == 0:
        raise RuntimeError("The table I found does not seem to have a head.")
    if len(headlist) > 1:
        warn("This table has more than one head.")
    head = headlist[0]
    bodylist = cal_table.find_all("tbody")
    if len(bodylist) == 0:
        raise RuntimeError("The table I found does not seem to have a body.")
    if len(bodylist) > 1:
        warn("This table has more than one body.")
    body = bodylist[0]

    return head, body

def get_calendar_table(url, fixfun=None):
    """
    Scraps calendar info from the given url.  You can pass a function that
    fixes bad date ranges.
    """

    if fixfun is None:
        fixfun = lambda rg: rg

    res = requests.get(url)
    res.raise_for_status()
    calendar_page = bs4.BeautifulSoup(res.text, "lxml")

    head, body = extract_table_parts(calendar_page)

    # Parse the table into dict of dicts, one for each semester:
    colnames = [col.getText() for col in head.find_all("th")]
    colcnt = len(colnames)

    semesters = {s:{} for s in colnames[1:]}

    for row in body.find_all("tr"):
        for i, cell in enumerate(row.find_all("td")):
            if i == 0:
                #key = unicodedata.normalize("NFKD",cell.getText())
                key = unidecode(cell.getText())
            elif i < colcnt:
                #dates = unicodedata.normalize("NFKD",cell.getText()).strip(" ")
                # Strip stupid comments they sometimes put in there
                stupid = cell.find("strong")
                if stupid:
                    _ = stupid.extract()
                dates = unidecode(cell.getText()).strip(" ")
                if dates != "":
                    daterange = parse(dates)
                    semesters[colnames[i]][key] = fixfun(daterange)

    return semesters

def fix_stupid_range(daterange):
    """Fix STUPID ranges from SVSU calendar, like Aug 29-2"""
    if daterange[1] is not None:
        delta = daterange[1] - daterange[0]
        if delta > timedelta(days=300):
            daterange = (daterange[0] + relativedelta(years=1),
                         daterange[1] + relativedelta(months=1))
    return daterange

def get_semester_data(semester, year=None):
    """Gets data on a single semester"""
    if semester == "Fall" or semester == "Winter":
        url = FALL_WINTER_URL
    elif semester == "Spring" or semester == "Summer":
        url = SPRING_SUMMER_URL
    else:
        raise ValueError("Invalid semester: {}".format(semester))

    if year is None:
        year = datetime.now().year

    key = "{} {}".format(semester, year)

    semesters = get_calendar_table(url, fix_stupid_range)

    if key in semesters:
        return semesters[key]

    warn("No info for {} semester!".format(key))
    return {}

# A convenience function for printing:

def date_range_str(daterange, fmt=None):
    """String with a single date is second is None, or range"""
    if fmt is None:
        fmt = "%m/%d/%Y"
    if daterange[1] is None:
        return daterange[0].strftime(fmt)
    else:
        return daterange[0].strftime(fmt) + " to " + daterange[1].strftime(fmt)

