from datetime import datetime
import json


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


def createRecord(row: str) -> dict:
    timestamp, satellite_id, red_high_limit, yellow_high_limit, yellow_low_limit, red_low_limit, raw_value, component = row.split(
        '|')

    record = {
        'satelliteId': int(satellite_id),
        'severity': createSeverity(float(red_high_limit), float(yellow_high_limit), float(yellow_low_limit), float(red_low_limit), float(raw_value)),
        'component': component,
        'timestamp': str(createTimestamp(timestamp).isoformat())[:-3] + 'Z',
    }

    return record


def fileToData(data: list[str]) -> list[dict]:
    result = [createRecord(status) for status in data]
    return result


def tstatRedHigh(data: dict) -> bool:
    return data['component'] == 'TSTAT' and data['severity'] == "RED HIGH"


def battRedLow(data: dict) -> bool:
    return data['component'] == 'BATT' and data['severity'] == "RED LOW"


def addToReport(report: dict, status: dict) -> dict:
    report[status['satelliteId']] = {
        'count': 0,
        'case': status
    }


def alertReport(data: list[dict]) -> list[dict]:
    """create a report dict based on minutes """
    batt_red_low = dict()
    tstat_red_high = dict()
    result = list()

    for status in data:
        if tstatRedHigh(status):
            if status['satelliteId'] not in tstat_red_high:
                addToReport(tstat_red_high, status)
            tstat_red_high[status['satelliteId']]['count'] += 1

            if tstat_red_high[status['satelliteId']]['count'] >= 3:
                result.append(tstat_red_high[status['satelliteId']]['case'])

        if battRedLow(status):
            if status['satelliteId'] not in batt_red_low:
                addToReport(batt_red_low, status)
            batt_red_low[status['satelliteId']]['count'] += 1

            if batt_red_low[status['satelliteId']]['count'] >= 3:
                result.append(batt_red_low[status['satelliteId']]['case'])
    print(batt_red_low)
    print(tstat_red_high)
    return result


def createAlertReport(data: list[dict]) -> dict[dict]:
    alertReport = {
        'BATT': {},
        'TSTAT': {},
    }
    batt_red_low = dict()
    tstat_red_high = dict()
    result = list()

    for status in data:
        if tstatRedHigh(status):
            addToReport(tstat_red_high, status)
            tstat_red_high[status['satelliteId']]['count'] += 1

            if tstat_red_high[status['satelliteId']]['count'] >= 3:
                result.append(tstat_red_high[status['satelliteId']]['case'])

        if battRedLow(status):
            if status['satelliteId'] not in batt_red_low:
                batt_red_low[status['satelliteId']] = {
                    'count': 0,
                    'case': status
                }
            batt_red_low[status['satelliteId']]['count'] += 1

            if batt_red_low[status['satelliteId']]['count'] >= 3:
                result.append(batt_red_low[status['satelliteId']]['case'])

    return result


data = fetchTxtFile("input.txt")
data = fileToData(data)
result = json.dumps(alertReport(data), indent=4)
print(result)
