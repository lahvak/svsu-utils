from yaml import load

# This was extracted from a pdf table downloaded from registrars website.  Lots
# of hand reformating was done to make it uniform and parseable.  That means
# errors may have been introduced.  Also, there may be changes from year to
# year.  Check the results against the official table.

yaml_data = """
Slots:
   - 8:30 am – 10:20 am
   - 10:30 am – 12:20 pm
   - 12:30 pm – 2:20 pm
   - 2:30 pm – 4:20 pm
   - 4:30 pm – 6:20 pm
   - 6:30 pm – 8:20 pm
   - 7:00 pm – 8:50 pm
   - 8:30 pm – 10:20 pm
Monday:
   - MWF, MW, MR at 8 or 8:30
   - MWF, MW, MR at 10 or 10:30
   - MWF, MW, MR at 12 or 12:30
   - MWF, MW, MR at 14 or 14:30
   - M, MWF, MW, MR at 16 or 16:30
   - MW, M at 18 or 18:30
   - MW, M at 19 or 19:30
   - MW, M at 20 or 20:30
Tuesday:
   - MTWR, MTRF, TR, TF at 8 or 8:30
   - MTWR, MTRF, TR, TF at 10 or 10:30
   - MTWR, MTRF, TR, TF at 12 or 12:30
   - MTWR, MTRF, TR, TF at 14 or 14:30
   - T, MTWR, MTRF, TR, TF at 16 or 16:30
   - TR, T at 18 or 18:30
   - TR, T at 19 or 19:30
   - TR, T at 20 or 20:30
Wednesday:
   - MWF, MW, WF at 9 or 9:30
   - MWF, MW, WF at 11 or 11:30
   - MWF, MW, WF at 13 or 13:30
   - MWF, MW, WF at 15 or 15:30
   - MWF, MW, WF at 17 or 17:30 OR W at 16
   - W at 18 or 18:30
   - W at 19 or 19:30
   - W at 20 or 20:30
Thursday:
   - MTWR, TR, MR at 9 or 9:30
   - MTWR, TR, MR at 11 or 11:30
   - MTWR, TR, MR at 13 or 13:30
   - MTWR, TR, MR at 15 or 15:30
   - MTWR, TR, MR at 17 or 17:30 OR R at 16
   - R at 18 or 18:30
   - R at 19 or 19:30
   - R at 20 or 20:30
Friday:
   - MTRF, TF at 9 or 9:30 OR WF at 8 or 8:30
   - MTRF, TF at 11 or 11:30 OR WF at 10 or 10:30
   - MTRF, TF at 13 or 13:30 OR WF at 12 or 12:30
   - MTRF, TF at 15 or 15:30 OR WF at 14 or 14:30
   - MTRF, TF at 17 or 17:30 OR WF at 16 or 16:30
   - WF, F at 18 or 18:30
   - WF, F at 19 or 19:30
   - WF, F at 20 or 20:30
"""

data = load(yaml_data)

def time_to_minutes(time):
    l = [int(s) for s in time.split(":")]
    return 60*l[0] + (l[1] if len(l) > 1 else 0)

def parse(v):
    l = [c.split(" at ") for c in v.split(" OR ")]
    l = [{'days': s[0].split(", "), 'times': [time_to_minutes(t) for t in s[1].split(" or ")]} for s in l]
    return(l)

slots = data["Slots"]

days = {day: [parse(v) for v in vals] for day, vals in data.items() if day != "Slots"}

def find_time(ds, t):
    time = time_to_minutes(t)

    for day, s in days.items():
        for i, l in enumerate(s):
            for option in l:
                if ds in option['days'] and time in option['times']:
                    return day, slots[i]

    return None, None

classes = {
    "103": ("TR", "10:30"),
    "120A": ("TR", "12:30"),
    "140": ("MW", "10:30"),
    "261": ("TR", "19"),
}

for k, v in classes.items():
    ex = find_time(*v)
    print("{}: {} at {}".format(k, ex[0], ex[1]))
