from svsu_calendar import get_semester_data, date_range_str

SEMESTER = "Fall"

for e, d in sorted(get_semester_data(SEMESTER).items(), key=lambda x: x[1][0]):
    print("{}: {}".format(e, date_range_str(d)))
