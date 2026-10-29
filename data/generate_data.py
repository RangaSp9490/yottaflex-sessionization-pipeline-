import argparse, csv, random
from datetime import datetime, timedelta, timezone
from pathlib import Path
FIELDS = ['event_id','user_id','event_type','event_timestamp']
def generate(path, count=1000, seed=42, edge_cases=True):
    rng=random.Random(seed); start=datetime(2026,1,1,tzinfo=timezone.utc); rows=[]
    user_count=max(5,min(1000,count//10 or 5))
    for i in range(count):
        t=start+timedelta(seconds=rng.randint(0,86400))
        rows.append({'event_id':f'evt_{i:08d}','user_id':f'user_{rng.randint(1,user_count):04d}',
          'event_type':rng.choice(['page_view','click','search','purchase','login']),
          'event_timestamp':t.isoformat().replace('+00:00','Z')})
    if edge_cases and rows:
        rows[0]['event_timestamp']=''
        if len(rows)>2:
            rows[1]['event_timestamp']='not-a-timestamp'; rows.append(dict(rows[2]))
    rng.shuffle(rows); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    return len(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',default='data/input/sample_events.csv'); p.add_argument('--count',type=int,default=1000); p.add_argument('--seed',type=int,default=42); p.add_argument('--no-edge-cases',action='store_true'); a=p.parse_args()
    print(f'Wrote {generate(a.output,a.count,a.seed,not a.no_edge_cases)} rows to {a.output}')
