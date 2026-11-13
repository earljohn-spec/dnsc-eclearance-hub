# Front-end Wireframes & QA Test Plan (R8, R17)

## Design Principles

- PWA: vanilla HTML/CSS/JS served by FastAPI static handler
- Mobile-first responsive (320px / 768px / 1024px)
- WCAG AA color contrast, 44px minimum touch targets
- JWT stored in sessionStorage (not localStorage)
- No front-end framework, no build step

## Screen Inventory

| Screen            | Route           | Role    | Key Features                                  |
| ----------------- | --------------- | ------- | --------------------------------------------- |
| Login             | /login          | All     | JWT auth, rate limit cooldown, generic errors |
| Student Dashboard | /dashboard      | Student | Progress bar, holds by office, deadline       |
| Clearance Slip    | /slip           | Student | QR code, signed token, PDF download           |
| Staff Holdings    | /staff/holdings | Staff   | Search, clear holds, office-filtered          |
| Admin Overview    | /admin          | Admin   | Summary cards, holds by office                |
| Admin Imports     | /admin/imports  | Admin   | Pipeline status, reject log, trigger          |
| Admin Reports     | /admin/reports  | Admin   | CSV/JSON/XML export                           |
| Admin Audit Log   | /admin/audit    | Admin   | Append-only viewer, filters                   |
| Slip Verification | /verify/{token} | Public  | QR scan result, no auth                       |

## Navigation Flow

[Login] -> JWT stored -> Role check
|-- Student -> [Dashboard] -> [Slip] -> [Verify]
|-- Staff -> [Holdings] -> Clear/View holds
|-- Admin -> [Overview] -> [Imports] / [Reports] / [Audit]

All routes except /login and /verify/{token} require valid JWT.

## QA Test Plan Summary

| Category                    | Tests  | Priority |
| --------------------------- | ------ | -------- |
| A: Auth & Authorization     | 15     | Critical |
| B: Hub API Endpoints        | 20     | Critical |
| C: Data Import Pipeline     | 12     | Critical |
| D: Security Controls        | 12     | Critical |
| E: External API Integration | 4      | High     |
| F: End-to-End User Flows    | 6      | Critical |
| **Total**                   | **69** |          |

## Key Test Cases by Category

### A: Auth (selected)

- A1: Valid login per role -> 200 + JWT
- A4-A5: Invalid credentials -> 401 generic (no enumeration)
- A6: Rate limit after 5 failures -> 429
- A8-A10: Cross-role access -> 403
- A13: Tampered JWT payload -> 401

### B: API (selected)

- B1: Student /me -> masked ID
- B6: Slip generation (cleared) -> 200 + token
- B7: Slip generation (active holds) -> 400
- B10: Tampered slip verification -> verified=false
- B14-B16: Report export all formats -> 200

### C: Pipeline (selected)

- C1: Valid manifests -> exit 0
- C2-C3: Tampered files -> exit 2, audit entry
- C5: Library rejects -> 7 records in reject_log
- C7: Accounting rejects -> 4 records in reject_log
- C12: Clearance computation -> correct counts

### D: Security (all 12)

See SECURITY.md for full list.

### F: E2E (selected)

- F1: Student full flow: login -> holds -> slip -> verify
- F3: Admin flow: imports -> reject log -> export
- F6: 10 concurrent logins -> no DB locks

## Execution Plan

| Phase              | When              | Who           |
| ------------------ | ----------------- | ------------- |
| Unit (A, B, D)     | Every commit (CI) | Front-end/QA  |
| Integration (C, E) | Every PR merge    | Data Eng + QA |
| Security (D)       | Weekly + pre-demo | Security Eng  |
| E2E (F)            | Week 17           | Full Team A   |
| Dry run            | Week 17           | Team A + B    |
