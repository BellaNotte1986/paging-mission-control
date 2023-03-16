from datetime import datetime, timedelta
import json

alert_report = {
    'TSTAT': {},
    'BATT': {},
}
result = list()
filename = "input.txt"
TSTAT = 'TSTAT'
BATT = 'BATT'


def fetchTxtFile(filename: str) -> list[str]:
    '''return a list of status telemetry data in lines'''
    with open(filename, "r") as file:
        # taking away \n at the end of each line
        status_telemetry_data = [line.rstrip() for line in file]

    return status_telemetry_data


def createTimestamp(timestamp: str) -> datetime:
    '''convert a string of time into a timestamp'''
    date, time = timestamp.split(" ")
    year, month, day = date[:4], date[4:6], date[6:]
    result = f"{year}-{month}-{day} {time}"
    return datetime.fromisoformat(result)


def createSeverity(red_high_limit: float, yellow_high_limit: float, yellow_low_limit: float, red_low_limit: float, raw_value: float) -> str:
    '''return alert label based on raw_value'''
    if raw_value > red_high_limit:
        return "RED HIGH"
    elif raw_value > yellow_high_limit:
        return "YELLOW HIGH"
    elif raw_value < red_low_limit:
        return "RED LOW"
    elif raw_value < yellow_low_limit:
        return "YELLOW LOW"
    return "NORMAL"


def createRecord(timestamp: datetime, satellite_id: str, red_high_limit: str, yellow_high_limit: str, yellow_low_limit: str, red_low_limit: str, raw_value: str, component: str) -> dict:
    record = {
        'satelliteId': int(satellite_id),
        'severity': createSeverity(float(red_high_limit), float(yellow_high_limit), float(yellow_low_limit), float(red_low_limit), float(raw_value)),
        'component': component,
        'timestamp': str(timestamp.isoformat())[:-3] + 'Z',
    }

    return record


def addRecord(row: str) -> None:
    timestamp, satellite_id, red_high_limit, yellow_high_limit, yellow_low_limit, red_low_limit, raw_value, component = row.split(
        '|')

    timestamp = createTimestamp(timestamp)

    record = createRecord(timestamp, satellite_id, red_high_limit, yellow_high_limit,
                          yellow_low_limit, red_low_limit, raw_value, component)

    if tstatRedHigh(record):
        countTwo(TSTAT, timestamp)
        alert_report[TSTAT][timestamp] = record

    if battRedLow(record):
        countTwo(BATT, timestamp)
        alert_report[BATT][timestamp] = record


def fileToReport(data: list[str]):
    for status in data:
        addRecord(status)


def tstatRedHigh(data: dict) -> bool:
    return data['component'] == 'TSTAT' and data['severity'] == "RED HIGH"


def battRedLow(data: dict) -> bool:
    return data['component'] == 'BATT' and data['severity'] == "RED LOW"


def withinTimespan(start: datetime, stop: datetime, minutes: int) -> bool:
    '''reutnr if time difference within the given timespan '''
    return (stop - start) // timedelta(minutes=1) <= minutes


def countTwo(component, timestamp):
    '''insert record to result when there are two previous alert'''
    count = 0
    on = True
    first = ""
    time_span = 5
    alert_limit = 2
    component_alert_report = alert_report[component]

    for time, record in component_alert_report.items():
        if(withinTimespan(timestamp, time, time_span)):
            # one time only, add the first found record to first
            if(on):
                first = record
                on = False
            count += 1

    if count >= alert_limit:
        if first not in result:
            result.append(first)


data = fetchTxtFile(filename)
data = fileToReport(data)

# convert report into json format
result = json.dumps(result, indent=4)
print(result)
