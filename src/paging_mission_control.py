from datetime import datetime

def fetchTxtFile(filename: str) -> list[str]:
  '''return a list of status telemetry data in lines'''
  with open(filename, "r") as file:
    # taking away \n at the end of each line
    status_telemetry_data = [line.rstrip() for line in file]
  
  return status_telemetry_data

def createTimestamp(timestamp: str) -> datetime:
  date, time = timestamp.split(" ")
  year, month, day = date[:4], date[4:6], date[6:]
  result = f"{year}-{month}-{day} {time}"
  return datetime.fromisoformat(result)

def createRecord(row: str) -> dict:
  timestamp, satellite_id, red_high_limit, yellow_high_limit, yellow_low_limit, red_low_limit, raw_value, component = row.split('|')
  record = {
      'timestamp': createTimestamp(timestamp),
      'satelliteId': satellite_id,
      'red_high_limit': float(red_high_limit), 
      'yellow_high_limit': float(yellow_high_limit),
      'yellow_low_limit': float(yellow_low_limit),
      'red_low_limit': float(red_low_limit),
      'raw_value': float(raw_value),
      'component': component,
    }
  return record

def fileToData(data: list[str]) -> list[dict]:
  result = list()
  
  for status in data:  
    result.append(createRecord(status))
  return result

def alert(data: list[dict]) -> list[dict]:
  pass
# print(os.getcwd())
data = fetchTxtFile("input.txt")
data = fileToData(data)
print(data[0])
print(data[0]['timestamp'].isoformat())