from datetime import datetime

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

def createSeverity(red_high_limit:float, yellow_high_limit:float, yellow_low_limit:float, red_low_limit:float, raw_value: float) -> str:
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
  timestamp, satellite_id, red_high_limit, yellow_high_limit, yellow_low_limit, red_low_limit, raw_value, component = row.split('|')
  
  record = {
      'satelliteId': int(satellite_id),
      'severity': createSeverity(float(red_high_limit), float(yellow_high_limit), float(yellow_low_limit), float(red_low_limit), float(raw_value)),
      'component': component,
      'timestamp': createTimestamp(timestamp),
    }
  
  return record

def fileToData(data: list[str]) -> list[dict]:
  result = [createRecord(status) for status in data]
  return result

def createAlert(status: dict) -> dict:
  
  return {}
def alert(data: list[dict]) -> list[dict]:
  alert_list = list()
  result = list()
  battery_voltage_below_red_low = dict()
  temperature_reading_exceed_red_high = dict()
  pass

  

data = fetchTxtFile("input.txt")
data = fileToData(data)
for line in data:
  print(line)
# print(data[0]['timestamp'].isoformat())