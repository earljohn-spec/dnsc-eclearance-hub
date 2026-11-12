# Data Mapping Specification (R9, R10)

## Common Target Schema (13 fields)

| Field            | Type       | Description                                                 |
| ---------------- | ---------- | ----------------------------------------------------------- |
| holding_id       | INTEGER PK | Auto-increment                                              |
| real_student_id  | TEXT       | YYYY-NNNN-NN                                                |
| student_name     | TEXT       | Full name                                                   |
| source_system    | TEXT       | library/accounting/registrar/student_affairs                |
| hold_type        | TEXT       | library_fine/tuition_balance/enrollment_status/disciplinary |
| hold_description | TEXT       | Human-readable reason                                       |
| amount           | REAL       | Monetary value (0.0 if N/A)                                 |
| status           | TEXT       | active/cleared                                              |
| date_placed      | TEXT       | ISO 8601                                                    |
| date_cleared     | TEXT       | ISO 8601 (nullable)                                         |
| cleared_by       | TEXT       | Staff ID (nullable)                                         |
| semester         | TEXT       | e.g. 2026-2027-1                                            |
| raw_data_hash    | TEXT       | SHA-256 of original record                                  |

## Source 1: Library (XML)

**File:** `library_export_2026-11-20.xml` (29 borrowers, 7 deliberate errors)

**Mapping:**
| XML Element | Target Field | Transform |
|---|---|---|
| borrower/@id | real_student_id | Validate YYYY-NNNN-NN |
| borrower/name | student_name | Strip whitespace |
| — | source_system | Hardcode "library" |
| — | hold_type | Hardcode "library_fine" |
| borrower/fine | amount | Cast to float |
| borrower/due_date | date_placed | Parse to ISO 8601 |
| borrower/semester | semester | Direct copy |

**Reject Conditions (7):**

1. Missing student ID attribute
2. Empty name element
3. Invalid date format (not YYYY-MM-DD)
4. Negative fine amount
5. Missing book title element
6. Duplicate borrower ID
7. Unparseable XML structure

## Source 2: Accounting (CSV)

**File:** `accounting_balances_2026-11-20.csv` (42 rows, 4 deliberate errors)

**Mapping:**
| CSV Column | Target Field | Transform |
|---|---|---|
| student_id | real_student_id | Validate format |
| student_name | student_name | Strip whitespace |
| balance | amount | Cast to float |
| semester | semester | Direct copy |
| — | source_system | Hardcode "accounting" |
| — | hold_type | Hardcode "tuition_balance" |

**Reject Conditions (4):**

1. Missing student_id column value
2. Non-numeric balance field
3. Negative balance value
4. Empty semester field

## Source 3: Registrar (JSON API)

**Endpoint:** `GET /api/students` from registrar_mock_api.py

**Mapping:**
| JSON Field | Target Field | Transform |
|---|---|---|
| student_id | real_student_id | Validate format |
| full_name | student_name | Direct copy |
| program | hold_description | Store as context |
| enrollment_status | status | "enrolled"→cleared, "irregular"→active |
| — | source_system | Hardcode "registrar" |
| — | hold_type | Hardcode "enrollment_status" |

**Reject Conditions:** Pydantic schema validation (missing fields, invalid status enum).

## Source 4: Student Affairs (Manual Entry)

**Endpoint:** `POST /api/student-affairs/records`

**Mapping:** Direct from Pydantic-validated request body. All fields required except amount.

**Reject Conditions:** Pydantic validation on form input (422 on failure).

## Reject Log Format

| Field         | Type       | Description                  |
| ------------- | ---------- | ---------------------------- |
| reject_id     | INTEGER PK | Auto-increment               |
| source_system | TEXT       | Which source                 |
| reject_reason | TEXT       | Specific condition triggered |
| raw_data      | TEXT       | Sanitized original record    |
| timestamp     | TEXT       | ISO 8601                     |

## Clearance Computation Logic

A student is **cleared** if and only if ALL holdings across ALL source systems have `status = 'cleared'`. A single active hold from any office blocks overall clearance.

## Report Export (R10)

`GET /api/reports/registrar?format={csv|json|xml}`

- **CSV:** Standard comma-separated with header row
- **JSON:** Array of objects
- **XML:** `<clearance_report><student>...</student></clearance_report>`
- All formats include: student_id, name, program, clearance_status, holds_by_office, date_computed
- Admin-only endpoint, logged in audit trail
