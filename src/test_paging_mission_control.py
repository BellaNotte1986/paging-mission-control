import paging_mission_control
import unittest
from datetime import datetime


class TestPagingMissionControl(unittest.TestCase):

    def test_createSeverity(self):
        self.assertEqual(paging_mission_control.createSeverity(
            10, 5, 2, 1, -1), "RED LOW")
        self.assertEqual(paging_mission_control.createSeverity(
            10, 5, 2, 1, 1.5), "YELLOW LOW")
        self.assertEqual(paging_mission_control.createSeverity(
            10, 5, 2, 1, 11), "RED HIGH")
        self.assertEqual(paging_mission_control.createSeverity(
            10, 5, 2, 1, 6), "YELLOW HIGH")
        self.assertEqual(paging_mission_control.createSeverity(
            10, 5, 2, 1, 5), "NORMAL")

    def test_createTimestamp(self):
        self.assertEqual(paging_mission_control.createTimestamp(
            "20180101 23:01:05.001"), datetime(2018, 1, 1, 23, 1, 5, 1000))

    def test_tstatRedHigh(self):
        # assume return true
        test_case1 = {'satelliteId': 1000, 'severity': 'RED HIGH',
                      'component': 'TSTAT', 'timestamp': '2018-01-01T23:01:38.001Z'}
        # assume return false
        test_case2 = {'satelliteId': 1001, 'severity': 'RED LOW',
                      'component': 'BATT', 'timestamp': '2018-01-01T23:05:07.421Z'}
        self.assertTrue(paging_mission_control.tstatRedHigh(test_case1))
        self.assertFalse(paging_mission_control.tstatRedHigh(test_case2))

    def test_battRedLow(self):
        # assume return true
        test_case1 = {'satelliteId': 1001, 'severity': 'RED LOW',
                      'component': 'BATT', 'timestamp': '2018-01-01T23:05:07.421Z'}
        # assume return false
        test_case2 = {'satelliteId': 1000, 'severity': 'RED HIGH',
                      'component': 'TSTAT', 'timestamp': '2018-01-01T23:01:38.001Z'}
        self.assertTrue(paging_mission_control.battRedLow(test_case1))
        self.assertFalse(paging_mission_control.battRedLow(test_case2))

    def test_withinTimespan(self):
        timespan = 5

        # assume return true
        test_start = datetime(2018, 1, 1, 23, 1, 5, 1000)
        test_stop = datetime(2018, 1, 1, 23, 5, 5, 1000)

        # assume return false
        test_start2 = datetime(2018, 1, 1, 23, 1, 5, 1000)
        test_stop2 = datetime(2018, 1, 1, 23, 59, 5, 1000)

        self.assertTrue(paging_mission_control.withinTimespan(
            test_start, test_stop, timespan))
        self.assertFalse(paging_mission_control.withinTimespan(
            test_start2, test_stop2, timespan))


if __name__ == '__main__':
    unittest.main()
