from yaml import load, SafeLoader as Loader
from datetime import timedelta
from pylatex.utils import escape_latex


def daterangeIncl(first, last):
    day = first
    while day <= last:
        yield day
        day = day + timedelta(1)


def caltext(day, text, type="caltext"):
    return "\\" + type + "{" + day.strftime("%-m/%-d/%Y") + \
        "}{" + escape_latex(text) + "}"


with open("holidays.yaml", 'r') as hfile:
    holidays = load(hfile, Loader)

start = holidays.pop("Classes Begin")["Start"]
end = holidays.pop("Classes End")["Start"]
weeks = (end - start).days//7 + 2

BOXSIZE = "{}in".format(6/weeks)

if end.weekday() >= 5:  # Make classes end on Friday
    end = end - timedelta(end.weekday() - 4)

print(r"""\documentclass[10pt,letterpaper]{article}
\usepackage[left=.8in, right=.8in, top=.7in, bottom=.6in]{geometry}
\usepackage{fontspec}
\setmainfont[Ligatures=TeX]{Vollkorn}
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
\newcommand*{\Holidays}{%""")

for hday, dates in holidays.items():
    if "End" in dates:
        for day in daterangeIncl(dates["Start"], dates["End"]):
            print(caltext(day, hday, "Holiday"))
    else:
        print(caltext(dates["Start"], hday, "Holiday"))

print(r"""}
\begin{document}
\begin{center}
""")

print("\\begin{calendar}{" +
      start.strftime("%-m/%-d/%Y") +
      "}}{{{}}}".format(weeks))

print("\\setlength{{\\calboxdepth}}{{{}}}".format(BOXSIZE))
print(r"""\calday[Monday]{\noclassday} % Monday
\calday[Tuesday]{\noclassday} % Tuesday
\calday[Wednesday]{\noclassday} % Wednesday
\calday[Thursday]{\noclassday} % Thursday
\calday[Friday]{\noclassday} % Friday
\skipday\skipday % weekend (no class)""")

print(caltext(start, "Classes Start"))
print(caltext(end, "Classes End"))

print(r"""
\Holidays
\end{calendar}
\end{center}
\newpage
\begin{center}
""")

print("\\begin{calendar}{" +
      start.strftime("%-m/%-d/%Y") +
      "}}{{{}}}".format(weeks))

print("\\setlength{{\\calboxdepth}}{{{}}}".format(BOXSIZE))

print(r"""
\MWClass
\Holidays
\end{calendar}
\end{center}
\newpage
\begin{center}
""")

print("\\begin{calendar}{" +
      start.strftime("%-m/%-d/%Y") +
      "}}{{{}}}".format(weeks))

print("\\setlength{{\\calboxdepth}}{{{}}}".format(BOXSIZE))

print(r"""
\TRClass
\Holidays
\end{calendar}
\end{center}
\end{document}""")
