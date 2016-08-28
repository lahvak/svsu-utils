"""
Module for parsing a class schedule.  Main interface is `parse_schedule`, that
takes a schedule file, holiday file, and few class parameters, creates a TeX
schedule file, and optionally posts schedule to Canvas.
"""
from warnings import warn
from markdown import markdown
import arrow
import yaml
import canvas

def holiday(day, end=None):
    """Creates a event time range."""
    start = day.floor('day')
    if end is None:
        end = day.ceil('day')
    else:
        end = end.ceil('day')

    return (start, end)

def is_holiday(day, holidays):
    """Tests if a day falls into one of given holiday time ranges."""
    return any(h[0] <= day <= h[1] in h for h in holidays)

def dates_to_holiday(dates):
    """Converts a yaml holiday times to a holiday range."""
    if "End" in dates:
        return holiday(arrow.get(dates['Start']), end=arrow.get(dates['End']))
    else:
        return holiday(arrow.get(dates['Start']))

def load_holidays(file):
    """Load holidays yaml file.  Returns a holiday list and starting day, if
    found in the file."""
    with open(file, 'r') as holidayfile:
        hdata = yaml.load(holidayfile)

    if "Classes Begin" in hdata:
        startdate = arrow.get(hdata["Classes Begin"]["Start"])
    else:
        startdate = None

    return startdate, {dates_to_holiday(dates): name for name, dates in hdata.items() if
                       name != "Classes Begin"}

def MW(start, weeks, holidays=None):
    """
    Assume start is Monday.
    """
    days = [day for day in arrow.Arrow.range("week", start, start.replace(weeks=+weeks))]
    wed = start.replace(days=+2)
    days += [day for day in arrow.Arrow.range("week", wed, wed.replace(weeks=+weeks))]

    if holidays is None:
        return sorted([day for day in days])

    return sorted([day for day in days if not is_holiday(day, holidays)])

def TR(start, weeks, holidays=None):
    """
    Assume start is Tuesday.
    """
    tue = start.replace(days=+1)
    days = [day for day in arrow.Arrow.range("week", tue, tue.replace(weeks=+weeks))]
    thu = tue.replace(days=+2)
    days += [day for day in arrow.Arrow.range("week", thu, thu.replace(weeks=+weeks))]

    if holidays is None:
        return sorted([day for day in days])

    return sorted([day for day in days if not is_holiday(day, holidays)])

def mkeventlist(events, dayfun, start, holidays, weeks=14):
    """Go trough list of events and schedule them into available dates,
    avoiding holidays."""
    i = iter(events)
    l = []
    for day in dayfun(start, weeks):
        if is_holiday(day, holidays):
            l.append(("", "Holiday"))
        else:
            try:
                l.append(next(i))
            except StopIteration:
                l.append("")
                warn("Not enough events scheduled")

    return l

funindex = {"MW": MW, "TR": TR}

TeXHead = r"""
\documentclass[10pt,letterpaper]{article}
\usepackage[left=.8in, right=.8in, top=.7in, bottom=.6in]{geometry}
\usepackage{fontspec}
\setmainfont[Mapping=tex-text]{Vollkorn}
\usepackage{microtype}
\usepackage{termcal}
\pagestyle{empty}
\thispagestyle{empty}
\newcommand{\TRClass}{%
\skipday % Monday (no class)
\calday[Tuesday]{\classday} % Tuesday
\skipday % Wednesday (no class)
\calday[Thursday]{\classday} % Thursday
\skipday % Friday 
\skipday\skipday % weekend (no class)
}
\newcommand{\MWClass}{%
\calday[Monday]{\classday} % Monday
\skipday % Tuesday (no class)
\calday[Wednesday]{\classday} % Wednesday
\skipday % Thursday (no class)
\skipday % Friday 
\skipday\skipday % weekend (no class)
}
\newcommand*{\Holiday}[2]{%
\options{#1}{\noclassday}
\caltext{#1}{#2}
}
"""

def TeXCalStart(startdate, dow, weeks=15):
    """Start of TeX calendar string. dow = TR or MW"""
    tex = r"\begin{document}\begin{center}\begin{calendar}{" + startdate + "}{"
    tex += str(weeks) + "}\\setlength{\\calboxdepth}{.3in}\\" + dow + "Class"
    return tex

def TeXCalEnd(holidays):
    """End of TeX calendar string."""
    tex = "%Holidays\n"
    for d, t in holidays.items():
        for day in arrow.Arrow.range('day', d[0], d[1]):
            tex += "\\Holiday{{{}}}{{{}}}\n".format(day.format('M/D/YYYY'), t)

    return tex + r"\end{calendar}\end{center}\end{document}"

def TeXCalItems(eventlist):
    """TeX representation of event list."""
    str1 = r"\caltexton{{1}}{{{}}}"
    str2 = r"\caltextnext{{{}}}"
    yield str1.format(eventlist[0][0])
    for s, _ in eventlist[1:]:
        yield str2.format(s)

def TeXCal(start, dow, events, holidays, weeks=15):
    """Put together all the infor and create a TeX calendar."""
    texstring = TeXCalStart(start, dow, weeks)
    texstring += "\n".join(list(TeXCalItems(events)))
    texstring += TeXCalEnd(holidays)
    return texstring

def write_tex_file(fn, start, dow, events, holidays, weeks=15):
    """Write TeX calendar into a file."""
    with open(fn, 'w') as texfile:
        texfile.writelines([TeXHead,
                            TeXCal(start, dow, events, holidays, weeks)])

def read_event_list(datafile):
    "Reads event list from a markdown file"
    with open(datafile, 'r') as data:
        schedule_str = data.read()

    days = [(lambda d: (d[0], markdown(d[1])))(s.split('\n',1))
            for s in schedule_str.split('\n## ')]

    # The first line will start with ## .  Remove it:
    if days[0][0][:3] == "## ":
        days[0] = (days[0][0][3:], days[0][1])

    return days

def parse_schedule(classid, datafile, holidayfile, dow, hour, minute,
                   length=110, post=False, manualstart=None):
    """
    Reads event list form datafile, holidays from holidayfile, and sets up a
    schedule.

    dow: day of week
    hour: starting hour on 24 hour format
    minute: starting minute
    length: class length in minutes
    post: if True, post on canvas
    manualstart: specify this is "Classes Begin" is not in holiday file
    """

    start, hdays = load_holidays(holidayfile)

    if start is None:
        if manualstart is not None:
            start = manualstart
        else:
            raise ValueError("No start date given!")

    event_list = read_event_list(datafile)

    write_tex_file("sched.tex", start.format("MM/DD/YYYY"), dow, event_list, hdays)

    el = mkeventlist(event_list, funindex[dow], start, hdays)

    if post and classid != 0:
        firstclass = canvas.firstclass(start.month, start.day, hour, minute)
        if dow == "TR":
            firstclass = firstclass.replace(days=+1)
        canvas.read_access_token()
        canvas.create_events_from_list(classid, el, firstclass, length)
