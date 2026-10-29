from datetime import datetime, timezone

REQUIRED_FIELDS = ('event_id', 'user_id', 'event_type', 'event_timestamp')

def parse_timestamp(value):
    if value is None or not str(value).strip():
        raise ValueError('missing_event_timestamp')
    raw = str(value).strip()
    if raw.endswith('Z'):
        raw = raw[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError('invalid_event_timestamp') from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def validate_and_deduplicate(rows):
    accepted, rejected, seen = [], [], set()
    for row_number, original in enumerate(rows, start=2):
        row = {str(k).strip(): ('' if v is None else str(v).strip()) for k, v in original.items()}
        reasons = [f'missing_{field}' for field in REQUIRED_FIELDS if not row.get(field, '')]
        timestamp = None
        if row.get('event_timestamp'):
            try:
                timestamp = parse_timestamp(row['event_timestamp'])
            except ValueError as exc:
                reasons.append(str(exc))
        event_id = row.get('event_id', '')
        if event_id and event_id in seen:
            reasons.append('duplicate_event_id')
        if reasons:
            rejected.append({**row, 'source_row_number': str(row_number), 'rejection_reason': ';'.join(reasons)})
            continue
        seen.add(event_id)
        row['_event_time'] = timestamp
        accepted.append(row)
    return accepted, rejected, len(rows)
