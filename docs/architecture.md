# Architecture and decisions

CSV source -> required-column check -> validation and duplicate detection -> event-time sorting/session assignment -> event/session/reject CSV outputs plus JSON report.

A new session starts when the gap from the immediately preceding event is greater than the timeout. Events are sorted by UTC event time and event ID. Invalid rows are retained in a reject file with reasons. Missing input columns fail fast because the input contract cannot be interpreted.

The implementation favors clarity and local reproducibility. For production, consider atomic output writes, persistent run metadata, schema versioning, and partitioned processing for data larger than memory.
