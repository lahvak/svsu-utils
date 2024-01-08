"""
Tools for creating TeX term calendars.
"""
from datetime import timedelta
from pylatex.utils import escape_latex

BEGIN_DOCUMENT = r"\begin{document}"
END_DOCUMENT = r"\end{document}"
NEWPAGE = r"\newpage"


def daterangeIncl(first, last):
    """
    Iterates through days from first to last, inclusive.
    """
    day = first
    while day <= last:
        yield day
        day = day + timedelta(1)


def caltext(day, text, type="caltext"):
    """
    Several LaTeX macros take the same format but have different
    names. The `type` argument is the csname.
    """
    return "\\" + type + "{" + day.strftime("%-m/%-d/%Y") + \
        "}{" + escape_latex(text) + "}"


def format_holidays(holidays):
    """
    Takes the holidays info from the YAML data and defines holidays
    for TeX calendar.
    """

    hdayTeX = "\\newcommand*{\\Holidays}{"
    for hday, dates in holidays.items():
        if "End" in dates:
            for day in daterangeIncl(dates["Start"], dates["End"]):
                hdayTeX += caltext(day, hday, "Holiday") + '\n'
        else:
            hdayTeX += caltext(dates["Start"], hday, "Holiday") + '\n'

    return hdayTeX + "}\n"


def get_dates(dates_yaml):
    """
    Get a yaml data with "Classes Begin", "Classes End" and
    all holidays.  Returns a tuple with starting date, ending date, and
    yaml with holidays only.
    """

    start = dates_yaml.pop("Classes Begin")["Start"]
    end = dates_yaml.pop("Classes End")["Start"]

    if end.weekday() >= 5:  # Make classes end on Friday
        end = end - timedelta(end.weekday() - 4)

    return (start, end, dates_yaml)


DAYS = {
    'M': 'Monday',
    'T': 'Tuesday',
    'W': 'Wednesday',
    'R': 'Thursday',
    'F': 'Friday',
}


def cal_days(days):
    """
    Takes a string of day abbreviations and defines
    calendar days.
    """

    caldays = ""
    for c in "MTWRF":
        if c in days:
            caldays += "\\calday[{}]{{\\classday}}\n".format(DAYS[c])
        else:
            caldays += "\\skipday\n"

    return caldays + "\\skipday\\skipday"


def calendar_text(command, text, escape=False):
    """
    takes a command string (either \\caltexton{i} or \\caltextnext)
    and text and creates a calendar day. The text must be in TeX format,
    if it is not, set `escape` to True.
    """

    if escape:
        text = escape_latex(text)

    return command + "{" + text + "}"


def calday_text(n, text, escape=False):
    """
    takes the day number (from 1) and text
    and creates a calendar day. The text must be in TeX format,
    if it is not, set `escape` to True.
    """

    return calendar_text(f"\\caltexton{{{n}}}", text, escape)


def calnext_text(text, escape=False):
    """
    Takes a text and creates a next calendar day.
    The text must be in TeX format, if it is not, set `escape` to True.
    """

    return calendar_text("\\caltextnext", text, escape)


def list_to_days(texts, escape=False):
    """
    Takes a list of calendar texts and creates a sequence of
    \\caltexton's and \\caltexnexts. The texts must be in TeX
    format, or `escape` must be set.
    """

    if not texts:
        return ""

    contents = [calday_text(1, texts[0], escape)]
    contents += [calnext_text(t, escape) for t in texts[1:]]

    return "\n".join(contents)


def preamble(holidays):
    """
    Returns TeX preamble for calendar.
    """
    return r"""\documentclass[10pt,letterpaper]{article}
\usepackage[left=.8in, right=.8in, top=.7in, bottom=.6in]{geometry}
\usepackage{fontspec}
\setmainfont[Ligatures=TeX]{Vollkorn}
\usepackage{termcal}
\pagestyle{empty}
\newcommand*{\Holiday}[2]{%
\options{#1}{\noclassday}
\caltext{#1}{#2}
}
""" + format_holidays(holidays)


def calendar(start, end, days, contents=None):
    """
    Creates a TeX calendar starting at `start`, ending at `end`, with days
    of week specified in `days`, with optional contents for
    classes, in TeX format.
    """

    # Make sure calendar start on Monday
    monday = start - timedelta(start.weekday())
    weeks = (end - monday).days//7 + 2
    boxsize = "{}in".format(6/weeks)

    calendar = "\n".join(
        [
            r"\begin{center}",
            r"\begin{calendar}{" +
            monday.strftime("%-m/%-d/%Y") + "}}{{{}}}".format(weeks),
            "\\setlength{{\\calboxdepth}}{{{}}}".format(boxsize),
            cal_days(days),
            caltext(start, "Classes Start"),
            caltext(end, "Classes End"),
            "\\Holidays\n",
            "" if contents is None else contents,
            r"\end{calendar}",
            r"\end{center}"
        ])

    return calendar
