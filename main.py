from satellite import Satellite
from dateutil import parser
import json

def main():

 satellite_dictionary = {} #dictionary of satellites (key = id, value = satellite)
 firstOccurences = [] #list of the first occurence of a violation 


 file = open("tests.txt", "r"); #reading the file with the test values

 for line in file: #read through each line in the file

  attributes = line.split("|") #in the text file, attributes are separated by '|'
  id = attributes[1]
  if id not in satellite_dictionary.keys(): #satellite is not in the dictionary yet, add it
   satellite_dictionary[id] = Satellite(id)
  satellite = satellite_dictionary.get(id) #satellite already exists in the dictionary, get it

  component = attributes[7]
  timestamp = parser.parse(attributes[0])
  raw_value = float(attributes[6])

  if component == 'BATT\n':
   component = "BATT"
   red_low_limit = float(attributes[5])
   if raw_value < red_low_limit: #violation has occured 
    satellite.battery_violation_counter += 1
    violation = {"satelliteId" : id, "severity" : "RED LOW", "component" : component, "timestamp" : timestamp}
    satellite.battery_violation_list.append(violation) #add violation to this satellites list

  if component == 'TSTAT\n':
   component = "TSTAT"
   red_high_limit = float(attributes[2])
   if raw_value > red_high_limit: #violation has occured
    satellite.temperature_violation_counter += 1
    violation = {"satelliteId" : id, "severity" : "RED HIGH", "component" : component, "timestamp" : timestamp}
    satellite.temperature_violation_list.append(violation) #add violation to this satellites list

  #after all lines have been read, see if there were 3+ violations
  #if there were, only need the first occurence of the 3 
 for satellite in satellite_dictionary.values():
  if satellite.temperature_violation_counter >= 3:
   firstOccurences.append(satellite.temperature_violation_list[0])
  if satellite.battery_violation_counter >= 3:
   firstOccurences.append(satellite.battery_violation_list[0])

  
 print(json.dumps(firstOccurences, default = str)) #conver to json. if an unknown type is found, conver to string
   
 file.close()

main()
