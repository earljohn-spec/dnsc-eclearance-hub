# Automation Script Design (R1, R2)

## Script Inventory

| #   | Script               | Language | Purpose                          | Trigger         |
| --- | -------------------- | -------- | -------------------------------- | --------------- |
| S1  | verify_manifests.py  | Python   | HMAC-SHA256 integrity check      | Pre-import gate |
| S2  | import_library.py    | Python   | Parse XML, validate, map, insert | Pipeline step 1 |
| S3  | import_accounting.py | Python   | Parse CSV, validate, map, insert | Pipeline step 2 |
| S4  | sync_registrar.py    | Python   | Pull JSON API, map, upsert       | Pipeline step 3 |
| S5  | run_all_imports.sh   | Bash     | Orchestrate S1-S6 with rollback  | Cron / manual   |
| S6  | compute_clearance.py | Python   | Compute per-student clearance    | Post-pipeline   |

## Pipeline Flow

[Cron 02:00 / Admin Trigger]
|
v
[S1: verify_manifests.py] -- Fail --> HALT (exit 2)
| Pass
v
[S2: import_library.py] -- Fail --> Log warning, continue
|
v
[S3: import_accounting.py] -- Fail --> Log warning, continue
|
v
[S4: sync_registrar.py] -- Fail --> Log warning, continue
|
v
[S6: compute_clearance.py]
|
v
[Complete: exit 0 (full) or 1 (partial)]

## Script Details

### S1: verify_manifests.py

- Reads `.sha256` manifest files from `data/`
- Verifies each data file using `hmac.compare_digest()`
- Halts entire pipeline on any mismatch (exit 2)
- Logs failure to audit log with truncated hash

### S2: import_library.py

- Parses `library_export_2026-11-20.xml` via `xml.etree.ElementTree`
- Applies 7 reject conditions (see DATA_MAPPING.md)
- Maps valid records to 13-field common schema
- Inserts via parameterized sqlite3 queries
- Retries on DB lock (3 attempts, exponential backoff)

### S3: import_accounting.py

- Reads `accounting_balances_2026-11-20.csv` via `csv.DictReader`
- Applies 4 reject conditions (see DATA_MAPPING.md)
- Handles encoding errors with `errors='replace'`
- Maps to common schema, inserts via parameterized queries

### S4: sync_registrar.py

- Calls `GET /api/students` on registrar mock API via `httpx`
- Authenticates with `X-API-Key` header from `.env`
- Validates response against Pydantic model
- Upserts: updates existing records, inserts new ones
- 10s timeout, 3 retries with exponential backoff
- Non-blocking: pipeline continues on failure

### S5: run_all_imports.sh

- Sources `.env`, activates venv, checks DB exists
- Runs S1-S4-S6 in strict sequence
- Checks exit codes: S1 failure halts, S2-S4 failure logs and continues
- Captures stdout/stderr to `logs/pipeline_YYYY-MM-DD_HHMMSS.log`
- Cron: `0 2 * * * /path/to/run_all_imports.sh`
- Manual: `POST /api/admin/run-imports`

### S6: compute_clearance.py

- Queries all holdings per student
- Marks "cleared" only if ALL holds across ALL sources are cleared
- Updates `clearance_status` table
- Generates summary CSV in `reports/`

## Security Integration

- All DB queries: parameterized (no string concatenation)
- File paths: whitelist-validated (no path traversal)
- `.env` loaded via python-dotenv (never hardcoded)
- Audit log entry per script execution
- Bash script runs with minimum filesystem permissions

## Team Assignments

| Script | Primary              | Support              |
| ------ | -------------------- | -------------------- |
| S1     | Security Engineer    | DevOps               |
| S2     | Data Integration Eng | DBA                  |
| S3     | Data Integration Eng | DBA                  |
| S4     | API Developer        | Data Integration Eng |
| S5     | Data Integration Eng | DevOps               |
| S6     | Data Integration Eng | Data Analyst         |
