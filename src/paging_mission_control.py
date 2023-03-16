from datetime import datetime, timedelta
import json

alertReport = {
    'TSTAT': {},
    'BATT': {},
}
result = list()


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
    if raw_value > red_high_limit:
        return "RED HIGH"
    elif raw_value > yellow_high_limit:
        return "YELLOW HIGH"
    elif raw_value < red_low_limit:
        return "RED LOW"
    elif raw_value < yellow_low_limit:
        return "YELLOW LOW"
    return "NORMAL"


def addRecord(row: str):
    timestamp, satellite_id, red_high_limit, yellow_high_limit, yellow_low_limit, red_low_limit, raw_value, component = row.split(
        '|')
    timestamp = createTimestamp(timestamp)
    record = {
        'satelliteId': int(satellite_id),
        'severity': createSeverity(float(red_high_limit), float(yellow_high_limit), float(yellow_low_limit), float(red_low_limit), float(raw_value)),
        'component': component,
        'timestamp': str(timestamp.isoformat())[:-3] + 'Z',
    }

    if tstatRedHigh(record):
        countThree('TSTAT', timestamp)
        alertReport['TSTAT'][timestamp] = record

    if battRedLow(record):
        countThree('BATT', timestamp)
        alertReport['BATT'][timestamp] = record


def fileToReport(data: list[str]):
    for status in data:
        addRecord(status)


def tstatRedHigh(data: dict) -> bool:
    return data['component'] == 'TSTAT' and data['severity'] == "RED HIGH"


def battRedLow(data: dict) -> bool:
    return data['component'] == 'BATT' and data['severity'] == "RED LOW"


def countThree(component, timestamp):
    count = 0
    on = True
    first = ""
    for time, record in alertReport[component].items():
        if(abs((timestamp - time) // timedelta(minutes=1)) <= 5):
          if(on):
            first = record
            on = False
          count+= 1
    if count >= 2:
      if first not in result:
        result.append(first)


data = fetchTxtFile("input.txt")
data = fileToReport(data)
result = json.dumps(result, indent=4)
print(result)
