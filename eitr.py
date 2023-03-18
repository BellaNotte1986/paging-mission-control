import json
import pprint
from datetime import datetime, timedelta

res = []
satellites = {}

def main(): 
    with open("/Users/supreeta/Desktop/input.txt", "r") as input_file:
        for line in input_file:
         
          # We split the line with | as the delimiter.

            timestamp, satellite_id, red_high, yellow_high, yellow_low, \
            red_low, raw_value, component = line.strip().split("|")
            satellite_id = int(satellite_id)
            timestamp = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S.%f")
            red_high = float(red_high)
            red_low = float(red_low)
            raw_value = float(raw_value)

            satellite_data = satellites.setdefault(satellite_id, {})
            component_data = satellite_data.setdefault(component, [])
            component_data.append((timestamp, raw_value)) # We add the timestamp and the value of each component for each satellite id
            
            #print(component_data)

            # We check if the value is lower than red_low value for the component BATT, then we add to a list called low. 
            # Based on the given condition in the question, if there are greater than or equal to 3 such values, 
            # we create an alert with the given attributes.
    
            if component == "BATT":
                low = [data[1] for data in component_data if data[1] < red_low]
                if len(low) >= 3:
                    alert = {
                        "satelliteId": satellite_id,
                        "severity": "RED_LOW",
                        "component": component,
                        "timestamp": timestamp.isoformat() + "Z"
                    }

                    res.append(json.dumps(alert))

# If the component is TSTAT, we check if the value is higher than the red_high, add such values to a list called high
# If there are 3 or more such values, we create an alert.
            elif component == "TSTAT":
                high = [data[1] for data in component_data if data[1] > red_high]
                if len(high) >= 3:
                    alert = {
                        "satelliteId": satellite_id,
                        "severity": "RED_HIGH",
                        "component": component,
                        "timestamp": timestamp.isoformat() + "Z"
                    }

                    res.append(json.dumps(alert))

# Here we remove any data points that are older than 5 minutes and hence not relevant.

            for component_data in satellite_data.values():
                component_data[:] = [data for data in component_data if timestamp - data[0] <= timedelta(minutes=5)]

if __name__ == '__main__':
    main()
    #When we pretty print this json object, we get the desired output.
    pprint.pprint(res)
    
