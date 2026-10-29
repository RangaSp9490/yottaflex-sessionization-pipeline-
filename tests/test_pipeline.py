import csv, tempfile, unittest
from pathlib import Path
from main import run_pipeline
class PipelineTests(unittest.TestCase):
    def test_counts_and_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'events.csv'
            with source.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=['event_id','user_id','event_type','event_timestamp']); w.writeheader()
                w.writerow({'event_id':'e1','user_id':'u1','event_type':'click','event_timestamp':'2026-01-01T10:00:00Z'})
                w.writerow({'event_id':'e2','user_id':'u1','event_type':'view','event_timestamp':'2026-01-01T10:05:00Z'})
                w.writerow({'event_id':'e3','user_id':'u1','event_type':'view','event_timestamp':''})
            out=root/'output'; r=run_pipeline(source,out,30); r2=run_pipeline(source,out,30)
            self.assertEqual((r['input_event_count'],r['accepted_unique_event_count'],r['rejected_event_count']),(3,2,1))
            self.assertTrue(all(r['reconciliation'].values())); self.assertEqual(r2['session_count'],1)
if __name__=='__main__': unittest.main()
