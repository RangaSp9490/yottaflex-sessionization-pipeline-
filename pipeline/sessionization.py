from collections import defaultdict
from datetime import timedelta

def assign_sessions(events, timeout_minutes=30):
    if timeout_minutes <= 0:
        raise ValueError('timeout_minutes must be greater than zero')
    by_user = defaultdict(list)
    for event in events:
        by_user[event['user_id']].append(event)
    assigned, summaries = [], []
    timeout = timedelta(minutes=timeout_minutes)
    for user_id in sorted(by_user):
        ordered = sorted(by_user[user_id], key=lambda e: (e['_event_time'], e['event_id']))
        session_no, previous, session_id, current = 0, None, None, []
        def finish():
            if not current:
                return
            times = [e['_event_time'] for e in current]
            summaries.append({'user_id': user_id, 'session_id': session_id,
                'session_start': min(times).isoformat().replace('+00:00', 'Z'),
                'session_end': max(times).isoformat().replace('+00:00', 'Z'),
                'event_count': len(current),
                'event_types': '|'.join(sorted({e['event_type'] for e in current}))})
        for e in ordered:
            t = e['_event_time']
            # Exact timeout boundary stays in the same session; greater gap starts a new one.
            if previous is None or t - previous > timeout:
                finish(); session_no += 1; session_id = f'{user_id}_S{session_no:03d}'; current = []
            assigned.append({'event_id': e['event_id'], 'user_id': e['user_id'], 'event_type': e['event_type'],
                'event_timestamp': t.isoformat().replace('+00:00', 'Z'), 'session_id': session_id})
            current.append(e); previous = t
        finish()
    assigned.sort(key=lambda e: (e['user_id'], e['event_timestamp'], e['event_id']))
    summaries.sort(key=lambda s: (s['user_id'], s['session_start'], s['session_id']))
    return assigned, summaries
