import paging_mission_control
import unittest

class TestPagingMissionControl(unittest.TestCase):
  
  def test_createSeverity(self):
    self.assertEqual(paging_mission_control.createSeverity(10,5,2,1,-1), "RED LOW")
    self.assertEqual(paging_mission_control.createSeverity(10,5,2,1,1.5), "YELLOW LOW")
    self.assertEqual(paging_mission_control.createSeverity(10,5,2,1,11), "RED HIGH")
    self.assertEqual(paging_mission_control.createSeverity(10,5,2,1,6), "YELLOW HIGH")
    self.assertEqual(paging_mission_control.createSeverity(10,5,2,1,5), "NORMAL")
    
if __name__ == '__main__':
  unittest.main()