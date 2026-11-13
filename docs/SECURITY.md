# Security Architecture Plan (R11-R16)

## Security Controls

| #   | Control               | Implementation                                     |
| --- | --------------------- | -------------------------------------------------- |
| R11 | Password Hashing      | bcrypt, 12 rounds                                  |
| R12 | Authentication        | JWT with HMAC-SHA256, 1-hour expiry                |
| R12 | Authorization         | RBAC: student, staff, admin                        |
| R13 | Input Validation      | Pydantic v2 models on all endpoints                |
| R13 | SQL Injection         | Parameterized sqlite3 queries exclusively          |
| R14 | Secrets Management    | .env + python-dotenv, never committed              |
| R14 | Transport Security    | HTTPS enforced on Railway                          |
| R14 | Manifest Verification | HMAC-SHA256 with hmac.compare_digest()             |
| R15 | Slip Signing          | HMAC-SHA256 signed tokens with expiry              |
| R15 | ID Masking            | Response-layer only: YYYY-\*\*\*\*-NN for students |
| R16 | Audit Logging         | Append-only table, no delete/update via API        |
| R16 | Rate Limiting         | 5 failed login attempts per 15-minute window       |

## Authentication Flow

1. Client sends plain-text password over HTTPS
2. Server retrieves stored bcrypt hash from database
3. Server compares using `bcrypt.checkpw()`
4. On success: generate JWT with `role` and `sub` claims, 1-hour expiry
5. On failure: return generic "Invalid credentials" (no user enumeration)
6. After 5 failures in 15 minutes: return 429 with 60-second cooldown

## RBAC Matrix

| Endpoint                      | Student | Staff  | Admin  |
| ----------------------------- | ------- | ------ | ------ |
| /api/auth/login               | Yes     | Yes    | Yes    |
| /api/clearance/me             | Yes     | No     | No     |
| /api/clearance/student/{id}   | No      | Yes    | Yes    |
| /api/clearance/deadline       | Yes     | Yes    | Yes    |
| /api/clearance/slip           | Yes     | No     | No     |
| /api/clearance/verify/{token} | Public  | Public | Public |
| /api/holdings/{id}            | No      | Yes    | Yes    |
| /api/student-affairs/records  | No      | Yes    | Yes    |
| /api/reports/registrar        | No      | No     | Yes    |
| /api/health                   | Public  | Public | Public |

## Security Test Cases (12)

| #   | Test                    | Method                           | Expected         |
| --- | ----------------------- | -------------------------------- | ---------------- |
| 1   | SQL injection in login  | POST `' OR 1=1 --`               | 401, no leak     |
| 2   | SQL injection in lookup | GET `/student/1; DROP TABLE`     | 400 or 404       |
| 3   | XSS in entry            | POST `<script>alert(1)</script>` | Sanitized        |
| 4   | Path traversal          | GET `../../etc/passwd`           | 400              |
| 5   | Oversized payload       | POST 10MB body                   | 413              |
| 6   | Missing fields          | POST empty body                  | 422              |
| 7   | Invalid types           | POST string in numeric           | 422              |
| 8   | HMAC timing             | Measure valid vs invalid         | No difference    |
| 9   | .env exposure           | GET `/.env`                      | 404              |
| 10  | Audit log delete        | DELETE `/audit`                  | 405              |
| 11  | Password storage        | Inspect DB directly              | All bcrypt       |
| 12  | ID masking              | GET `/clearance/me`              | YYYY-\*\*\*\*-NN |

## Audit Log Schema

| Field      | Type       | Description                           |
| ---------- | ---------- | ------------------------------------- |
| log_id     | INTEGER PK | Auto-increment                        |
| timestamp  | TEXT       | ISO 8601                              |
| actor_role | TEXT       | student/staff/admin/system            |
| actor_id   | TEXT       | Real ID (internal only)               |
| action     | TEXT       | LOGIN/LOGOUT/CLEAR/EXPORT/IMPORT/SLIP |
| target     | TEXT       | Resource affected                     |
| status     | TEXT       | success/failure                       |

Append-only: no UPDATE or DELETE operations permitted via any API endpoint.
