from svsu_calendar import get_semester_data
from yaml import dump

SEMESTER = "Fall"

UNWANTED_EVENTS = [
        "Commencement",
        "Classes Resume",
        ]


def daterange_to_yaml(daterange):
    """Converts a tuple into a dict with 'Start' and optional 'End' keys"""
    if daterange[1] is None:
        return {'Start': daterange[0].date()}

    return {'Start': daterange[0].date(), 'End': daterange[1].date()}


def semester_to_yaml(semester):
    """Prepares semester data for exporting as YAML"""
    return {k: daterange_to_yaml(d) for k, d in semester.items()
            if k not in UNWANTED_EVENTS}


with open("holidays.yaml", "w") as yf:
    dump(semester_to_yaml(
        get_semester_data(SEMESTER)), yf, default_flow_style=False
        )
