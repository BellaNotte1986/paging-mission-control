#Satellite class
class Satellite:
 def __init__(self, sat_id):
  self.id = sat_id
  self.temperature_violation_counter = 0 #number of temp violations
  self.battery_violation_counter = 0 #number of batt violations
  self.temperature_violation_list = [] #list of all temp violations for this satellite
  self.battery_violation_list = [] #list of all batt violations for this satellite
 
