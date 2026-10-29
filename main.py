import argparse, csv, logging, time, uuid
from pathlib import Path
from config import SESSION_TIMEOUT_MINUTES
from pipeline.validation import validate_and_deduplicate
from pipeline.sessionization import assign_sessions
from pipeline.reporting import write_csv, write_json, utc_now

EVENT_FIELDS = ['event_id','user_id','event_type','event_timestamp']
SESSION_FIELDS = ['user_id','session_id','session_start','session_end','event_count','event_types']
REJECT_FIELDS = EVENT_FIELDS + ['source_row_number','rejection_reason']

def read_events(path):
    with Path(path).open('r', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError('Input CSV must contain a header row.')
        missing = set(EVENT_FIELDS) - set(reader.fieldnames)
        if missing:
            raise ValueError('Missing required CSV columns: ' + ', '.join(sorted(missing)))
        return list(reader)

def run_pipeline(input_path, output_dir, timeout_minutes=SESSION_TIMEOUT_MINUTES):
    start = time.perf_counter(); run_id = str(uuid.uuid4())
    logging.info('run_id=%s starting input=%s', run_id, input_path)
    raw = read_events(input_path)
    accepted, rejected, input_count = validate_and_deduplicate(raw)
    assigned, sessions = assign_sessions(accepted, timeout_minutes)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    write_csv(out/'events_with_sessions.csv', assigned, EVENT_FIELDS + ['session_id'])
    write_csv(out/'sessions.csv', sessions, SESSION_FIELDS)
    write_csv(out/'rejected_events.csv', rejected, REJECT_FIELDS)
    report = {'run_id': run_id, 'run_started_at_utc': utc_now(), 'input_path': str(input_path),
        'session_timeout_minutes': timeout_minutes, 'input_event_count': input_count,
        'accepted_unique_event_count': len(accepted), 'rejected_event_count': len(rejected),
        'assigned_event_count': len(assigned), 'session_count': len(sessions),
        'reconciliation': {'input_equals_accepted_plus_rejected': input_count == len(accepted)+len(rejected),
            'accepted_equals_assigned': len(accepted) == len(assigned)},
        'runtime_seconds': round(time.perf_counter()-start, 6), 'status': 'success'}
    write_json(out/'quality_report.json', report)
    logging.info('run_id=%s complete accepted=%d rejected=%d sessions=%d', run_id, len(accepted), len(rejected), len(sessions))
    return report

def main():
    p = argparse.ArgumentParser(description='Convert event CSV rows into user sessions.')
    p.add_argument('--input', default='data/input/sample_events.csv'); p.add_argument('--output-dir', default='output')
    p.add_argument('--timeout-minutes', type=int, default=SESSION_TIMEOUT_MINUTES)
    p.add_argument('--log-level', choices=['DEBUG','INFO','WARNING','ERROR'], default='INFO')
    a = p.parse_args()
    logging.basicConfig(level=getattr(logging, a.log_level), format='%(asctime)s %(levelname)s %(message)s')
    r = run_pipeline(a.input, a.output_dir, a.timeout_minutes)
    print(f"Pipeline {r['status']}: {r['accepted_unique_event_count']} accepted, {r['rejected_event_count']} rejected, {r['session_count']} sessions.")
    print(f'See {a.output_dir}/quality_report.json for metrics.')
if __name__ == '__main__': main()
