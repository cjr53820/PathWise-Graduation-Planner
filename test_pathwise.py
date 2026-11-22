"""Run with python -m unittest discover -v; all test records are fictional."""
import unittest
from copy import deepcopy
from engine import STUDENTS, CATALOG, REQUIRED, audit, timeline, parse_course_list
from app import authenticate,can_read
class TestEngine(unittest.TestCase):
 def setUp(self): self.maya=deepcopy(STUDENTS['s1001'])
 def test_sample_total(self):self.assertEqual(audit(self.maya)['total'],40)
 def test_maya_earned(self):self.assertEqual(audit(self.maya)['earned'],18)
 def test_maya_transfer_source(self):self.assertIn('Northern Virginia',next(x['source'] for x in audit(self.maya)['rows'] if x['code']=='ENG 102'))
 def test_ready_course(self):self.assertEqual(next(x['status'] for x in audit(self.maya)['rows'] if x['code']=='CSC 301'),'Ready')
 def test_capstone_blocked(self):self.assertEqual(next(x['status'] for x in audit(self.maya)['rows'] if x['code']=='CSC 490'),'Blocked')
 def test_timeline_order(self):
  result=timeline(self.maya); positions={c['code']:i for i,t in enumerate(result['terms']) for c in t['courses']}
  self.assertLess(positions['CSC 301'],positions['CSC 380']);self.assertLess(positions['CSC 380'],positions['CSC 490'])
 def test_delay_alert(self):self.assertTrue(timeline(STUDENTS['s1002'])['delay'])
 def test_scenario_isolation(self):
  before=deepcopy(self.maya);timeline(self.maya,load=4,proposed=['CSC 301']);self.assertEqual(before,self.maya)
 def test_repeat_scenarios(self):
  first=timeline(self.maya,load=4);timeline(self.maya,load=1);self.assertEqual(first,timeline(self.maya,load=4))
 def test_blocked_priority(self):
  with self.assertRaisesRegex(ValueError,'needs CSC 380'):timeline(self.maya,proposed=['CSC 490'])
 def test_invalid_code(self):
  with self.assertRaisesRegex(ValueError,'not in the demo catalog'):parse_course_list(['CSC 999'])
 def test_duplicate_course(self):
  with self.assertRaisesRegex(ValueError,'more than once'):parse_course_list(['CSC 301','CSC 301'])
 def test_invalid_load(self):
  for val in [0,6]:
   with self.subTest(val=val),self.assertRaises(ValueError):timeline(self.maya,load=val)
 def test_transfer_not_double_counted(self):
  self.maya['completed'].append('ENG 102');self.assertEqual(audit(self.maya)['earned'],18)
 def test_authentication(self):self.assertEqual(authenticate('maya','Demo123!'),'maya')
 def test_invalid_login(self):self.assertIsNone(authenticate('maya','wrong'))
 def test_student_privacy(self):self.assertFalse(can_read('maya','s1002'))
 def test_advisor_permission(self):self.assertTrue(can_read('drivers','s1001'));self.assertFalse(can_read('drivers','s1003'))
 def test_unknown_student(self):self.assertFalse(can_read('drivers','s9999'))
 def test_elective_gap(self):self.assertEqual(timeline(self.maya)['remaining_elective_credits'],0)
if __name__=='__main__':unittest.main()
