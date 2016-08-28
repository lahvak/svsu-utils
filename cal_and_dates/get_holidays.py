from svsu_calendar import get_semester_data
from yaml import dump

SEMESTER = "Fall"

def daterange_to_yaml(daterange):
    """Converts a tuple into a dict with 'From' and optional 'To' keys"""
    if daterange[1] is None:
        return {'From': daterange[0].date()}
    else:
        return {'From': daterange[0].date(), 'To': daterange[1].date()}

def semester_to_yaml(semester):
    """Prepares semester data for exporting as YAML"""
    return {k:daterange_to_yaml(d) for k, d in semester.items()}

with open("holidays.yaml", "w") as yf:
    dump(semester_to_yaml(get_semester_data(SEMESTER)), yf, default_flow_style=False)
