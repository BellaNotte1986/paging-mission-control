import json
from datetime import datetime, timedelta

# Formats and constants
THREE_LOW_VOLTAGE = 3
THREE_HIGH_TEMPERATURE = 3

RED_HIGH = "RED HIGH"
RED_LOW = "RED LOW"

DATETIME_FORMAT = "%Y%m%d %H:%M:%S.%f"

FIVE_MINUTES = timedelta(minutes=5)

satellites = {}
output = []

def main(): 
    with open("input.txt", "r") as input_file:
        for line in input_file:
            # Parse line
            timestamp_str, satellite_id_str, red_high_str, yellow_high_str, yellow_low_str, red_low_str, raw_value_str, component = line.strip().split("|")

            # Convert timestamp and id
            timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
            satellite_id = int(satellite_id_str)

            red_high = float(red_high_str)
            red_low = float(red_low_str)
            raw_value = float(raw_value_str)

            # Update the status telemetry data for this satellite and component
            satellite_data = satellites.setdefault(satellite_id, {})
            component_data = satellite_data.setdefault(component, [])
            component_data.append((timestamp, raw_value))

            # Check for the violation conditions for this component
            if component == "BATT":
                low_voltages = [data[1] for data in component_data if data[1] < red_low]
                if len(low_voltages) >= THREE_LOW_VOLTAGE:
                    alert = {
                        "satelliteId": satellite_id,
                        "severity": RED_LOW,
                        "component": component,
                        "timestamp": timestamp.isoformat() + "Z"
                    }
                    
                    output.append(json.dumps(alert))

            elif component == "TSTAT":
                high_temperatures = [data[1] for data in component_data if data[1] > red_high]
                if len(high_temperatures) >= THREE_HIGH_TEMPERATURE:
                    alert = {
                        "satelliteId": satellite_id,
                        "severity": RED_HIGH,
                        "component": component,
                        "timestamp": timestamp.isoformat() + "Z"
                    }
                    
                    output.append(json.dumps(alert))

            # Remove the status telemetry data that is older than five minutes
            for component_data in satellite_data.values():
                component_data[:] = [data for data in component_data if timestamp - data[0] <= FIVE_MINUTES]
    
if __name__ == '__main__':
    main()
    print(output)