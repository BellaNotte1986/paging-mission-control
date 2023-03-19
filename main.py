from datetime import datetime, timedelta, time
import json


def parse_file(file_name):
    with open(file_name, "r") as file:
        data = [line.strip() for line in file.readlines()]

    time_index = 0
    id_index = 1
    comp_index = 7
    raw_value_i = 6
    red_high_i = 2
    red_low_i = 5

    # Key is component, value is (time, count) where time is the last time it was high/low and count is how many times it occured within last 5 mins
    batt_tracker = {}
    tstat_tracker = {}
    answer = []
    batt_lst = []
    tstat_lst = []

    for d in data:
        component = d[comp_index]
        if component == "BATT":
            batt_lst.append(d)
        else:
            tstat_lst.append(d)
    for d in data:

        lst = d.split("|")
        id_num = lst[id_index]
        date = lst[time_index]
        component = lst[comp_index]
        raw_value = float(lst[raw_value_i])
        red_high = float(lst[red_high_i])
        red_low = float(lst[red_low_i])

        if component == "BATT":

            if raw_value < red_low:
                last_time, count = batt_tracker.get(
                    component, (datetime(1, 1, 1, 0, 0, 0, 0), 1))
                curr_time = datetime.strptime(date, "%Y%m%d %H:%M:%S.%f")

                if abs(curr_time-last_time) <= timedelta(minutes=5):
                    count += 1
                    batt_tracker[component] = (last_time, count)
                else:
                    batt_tracker[component] = (curr_time, 1)

                if count == 3:
                    answer.append({
                        "satelliteId": id_num,
                        "severity": "RED LOW",
                        "component": "BATT",
                        "timestamp": batt_tracker[component][0].strftime("%Y%m%d %H:%M:%S.%f")
                    })
                    batt_tracker[component] = (
                        datetime(1, 1, 1, 0, 0, 0, 0), 1)

        else:
            if raw_value > red_high:
                last_time, count = tstat_tracker.get(
                    component, (datetime(1, 1, 1, 0, 0, 0, 0), 1))
                curr_time = datetime.strptime(date, "%Y%m%d %H:%M:%S.%f")

                if abs(curr_time-last_time) <= timedelta(minutes=5):
                    count += 1
                    tstat_tracker[component] = (last_time, count)
                else:
                    tstat_tracker[component] = (curr_time, 1)

                if count == 3:
                    answer.append({
                        "satelliteId": id_num,
                        "severity": "RED HIGH",
                        "component": "TSTAT",
                        "timestamp": tstat_tracker[component][0].strftime("%Y%m%d %H:%M:%S.%f")
                    })
                    tstat_tracker[component] = (
                        datetime(1, 1, 1, 0, 0, 0, 0), 1)

    return answer


for item in parse_file("sample.txt"):
    json_data = json.dumps(item)
    print(json_data)
