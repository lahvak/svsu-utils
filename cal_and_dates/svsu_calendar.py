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
# example Fall 2021 is labeled as "fall2021", but all other fall semesters are
# labeled as "fall2022" regardless of the year...

# Update in January 2025 - "The saga continues": This time it looks like all
# fall semesters are labeled as "fall2025", including the 2024 one and 2026
# one, while all non-fall semesters are labeled as ".*2026", again regardless
# of actual year.
#
# It seems like the only way to handle this is:
#
# 1. Find the table for the correct academic year. It will have a thead in
#    which the first cell contains the text "FALL ...." where .... is the year
#    of the fall semester of that academic year.

# 2. If we now restrict ourselves to that table only, there seems to be a way
#    to identify which semester a row belongs to: most of them will have a cell
#    that has a `header` attribute with, for example, "winter2026" for a winter
#    semester (the 2026 is regardless of the actual year). Some don't, but
#    these seem to have a cell with a `header` attribute that contains the name
#    of the semester, but with an uppercase first letter. Hopefully these two
#    cases cover everything.
#
# This would be so much easier if they would either put each semester in its
# own table with clearly labeled header, or include in each row an attribute
# that would uniquely indicate which semester does the row belong to.


def match_table(row, regexp):
    headlist = row.find_all("thead")
    if len(headlist) == 0:
        return False
    head = headlist[0]
    cells = head.find_all("td")
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
    Find the table for the academic year starting with FALL.
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
    data = row.find_all("td")
    if len(data) < 3:
        event = ""
        dates = ""
    else:
        event = data[0].getText().strip()
        dates = data[2].getText().strip()

    if dates:
        dates = parse(dates)

    return {'event': event, 'dates': dates}


def match_row(row, semesterreg):
    return len(row.find_all("td", headers=semesterreg)) > 0


def get_calendar_table(url, semester, year):
    """
    Scraps calendar info from the given url.  You can pass a function that
    fixes bad date ranges.
    """

    res = requests.get(url)
    res.raise_for_status()
    calendar_page = bs4.BeautifulSoup(res.text, "lxml")

    body = find_table(calendar_page, semester, year)

    semesterreg = re.compile(semester.lower()[1:])

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
