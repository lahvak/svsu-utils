"""
Scraps important semester dates from SVSU registrars calendar webpage
"""
from datetime import datetime
import requests
import bs4
import re
from daterangeparser import parse

URL = "https://www.svsu.edu/academicandstudentaffairs/calendar/academiccalendar/"

# It seems like this should be as easy as extracting all table rows that have
# an attribute "headers" with value that is the semester in question, but
# whoever coded this page was an idiot and the rows are weirdly mislabeled. For
# example Fall 2021 id labeled as "fall2021", but all other fall semesters are
# labeled as "fall2022" regardless of the year...


def match_table(row, regexp):
    headlist = row.find_all("thead")
    if len(headlist) == 0:
        return False
    head = headlist[0]
    cells = head.find_all("th")
    if len(cells) == 0:
        return False

    if regexp.match(cells[0].getText()) is None:
        return False

    return True


def semester_regex(semester, year):
    regstr = "{}\\s{{1,}}{}".format(semester.upper(), year)
    return re.compile(regstr)


def find_table(page, semester, year):
    """
    Extract body from the calendar table on the given page.
    It will give you the whole freaking academic year!
    You will need to filter it more.
    """
    # Find the calendar table
    tables = page.find_all("table")
    # The page was really coded by an idiot!
    semester = semester.upper()
    if semester != "FALL":
        semester = "FALL"
        year = year - 1
    regexp = semester_regex(semester, year)
    for t in tables:
        if match_table(t, regexp):
            return t.find("tbody")

    raise RuntimeError("Could not find a calendar table for {} {}".format(
        semester, year))


def parse_row(row):
    headers = row.find_all("th")
    data = row.find_all("td")
    if len(headers) == 0:
        event = ""
    else:
        event = headers[0].getText().strip()

    if len(data) < 2:
        dates = ""
    else:
        dates = data[1].getText().strip()

    if dates:
        dates = parse(dates)

    return {'event': event, 'dates': dates}


def match_row(row, semesterreg):
    return len(row.find_all("th", headers=semesterreg)) > 0


def get_calendar_table(url, semester, year):
    """
    Scraps calendar info from the given url.  You can pass a function that
    fixes bad date ranges.
    """

    res = requests.get(url)
    res.raise_for_status()
    calendar_page = bs4.BeautifulSoup(res.text, "lxml")

    body = find_table(calendar_page, semester, year)

    semesterreg = re.compile(semester.lower())

    return [parse_row(row) for row in body.find_all("tr")
            if match_row(row, semesterreg)]


def get_semester_data(semester, year=None):
    """Gets data on a single semester"""

    if year is None:
        year = datetime.now().year

    rows = get_calendar_table(URL, semester, year)

    return {row['event']: row['dates'] for row in rows if row['event']}

# A convenience function for printing:


def date_range_str(daterange, fmt=None):
    """String with a single date is second is None, or range"""
    if fmt is None:
        fmt = "%m/%d/%Y"
    if daterange[1] is None:
        return daterange[0].strftime(fmt)
    else:
        return daterange[0].strftime(fmt) + " to " + daterange[1].strftime(fmt)
