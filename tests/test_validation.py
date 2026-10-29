import unittest
from pipeline.validation import validate_and_deduplicate, parse_timestamp
class ValidationTests(unittest.TestCase):
    def test_missing_and_invalid_timestamps(self):
        rows=[{'event_id':'1','user_id':'u','event_type':'click','event_timestamp':''},{'event_id':'2','user_id':'u','event_type':'click','event_timestamp':'bad'}]
        a,r,n=validate_and_deduplicate(rows); self.assertEqual((len(a),len(r),n),(0,2,2))
        self.assertIn('missing_event_timestamp',r[0]['rejection_reason']); self.assertIn('invalid_event_timestamp',r[1]['rejection_reason'])
    def test_duplicate(self):
        row={'event_id':'1','user_id':'u','event_type':'click','event_timestamp':'2026-01-01T00:00:00Z'}
        a,r,_=validate_and_deduplicate([row,row]); self.assertEqual((len(a),len(r)),(1,1)); self.assertIn('duplicate_event_id',r[0]['rejection_reason'])
    def test_naive_timestamp_is_utc(self):
        self.assertEqual(parse_timestamp('2026-01-01T12:00:00').isoformat(),'2026-01-01T12:00:00+00:00')
if __name__=='__main__': unittest.main()
