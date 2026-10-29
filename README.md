# YottaFlex Event Sessionization Pipeline

A local, dependency-free Python solution for transforming clickstream/application events into user sessions using event-time gaps.

## Assumptions
- Input CSV columns: `event_id`, `user_id`, `event_type`, `event_timestamp`.
- Timestamps are ISO-8601; `Z` is accepted and naive timestamps are interpreted as UTC.
- Default timeout is 30 minutes. A new session begins only when the gap is **greater than** the timeout; an exact 30-minute gap stays in the same session.
- Events are sorted by timestamp then event ID for deterministic tie-breaking.
- First valid occurrence of an event ID wins; later duplicates are rejected.
- Invalid records are recorded in `rejected_events.csv`; output files are overwritten on each run.
- Session IDs are deterministic for identical accepted data and configuration.

## Requirements
Python 3.10+. No third-party packages required.

## Run
```bash
python data/generate_data.py --count 1000 --seed 42
python main.py --input data/input/sample_events.csv --output-dir output --timeout-minutes 30
```

Outputs: `output/events_with_sessions.csv`, `output/sessions.csv`, `output/rejected_events.csv`, `output/quality_report.json`.

Larger-data run:
```bash
python data/generate_data.py --count 100000 --seed 42 --no-edge-cases
python main.py --input data/input/sample_events.csv --output-dir output
```

## Tests
```bash
python -m unittest discover -s tests -v
```

## Design
CSV ingestion -> required-column check -> row validation/deduplication -> event-time sorting/session assignment -> CSV outputs and JSON reconciliation report. The report checks `input == accepted + rejected` and `accepted == assigned`, and records runtime and a run ID.

## Complexity and limitations
Per-user sorting is approximately O(n log n) time and O(n) memory. This is suitable for local assessment data, not unlimited streaming. Production improvements could include atomic output writes, persistent run metadata, schema versioning, and partitioned processing.

See `docs/architecture.md` and `docs/ai_usage.md`. Update AI disclosure with your actual prompts, review, changes, and tests before submission.
