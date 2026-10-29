import unittest
from pipeline.validation import validate_and_deduplicate
from pipeline.sessionization import assign_sessions
def ev(i,t,u='u1'):
    return {'event_id':i,'user_id':u,'event_type':'click','event_timestamp':t}
class SessionTests(unittest.TestCase):
    def test_out_of_order(self):
        a,_,_=validate_and_deduplicate([ev('b','2026-01-01T10:05:00Z'),ev('a','2026-01-01T10:00:00Z')]); assigned,s=assign_sessions(a,30)
        self.assertEqual(len(s),1); self.assertEqual([x['event_id'] for x in assigned],['a','b'])
    def test_exact_boundary_stays_same(self):
        a,_,_=validate_and_deduplicate([ev('a','2026-01-01T10:00:00Z'),ev('b','2026-01-01T10:30:00Z')]); _,s=assign_sessions(a,30); self.assertEqual(len(s),1)
    def test_greater_boundary_splits(self):
        a,_,_=validate_and_deduplicate([ev('a','2026-01-01T10:00:00Z'),ev('b','2026-01-01T10:30:01Z')]); _,s=assign_sessions(a,30); self.assertEqual(len(s),2)
    def test_users_separate(self):
        a,_,_=validate_and_deduplicate([ev('a','2026-01-01T10:00:00Z','u1'),ev('b','2026-01-01T10:00:00Z','u2')]); _,s=assign_sessions(a,30); self.assertEqual(len(s),2)
    def test_bad_timeout(self):
        with self.assertRaises(ValueError): assign_sessions([],0)
if __name__=='__main__': unittest.main()
