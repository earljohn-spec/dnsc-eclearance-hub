# Demo Script & Deployment Plan (R4, R18)

## Deployment

**Platform:** Railway (auto HTTPS, Python support, free tier)
**Services:** `clearance-hub` (FastAPI) + `registrar-mock` (Flask, internal only)
**Database:** SQLite on Railway persistent volume
**Secrets:** Railway dashboard only, never in repository

### Environment Variables

| Variable                   | Description             |
| -------------------------- | ----------------------- |
| DATABASE_URL               | SQLite file path        |
| JWT_SECRET_KEY             | 256-bit random hex      |
| REGISTRAR_API_KEY          | Service-to-service key  |
| HMAC_SECRET_KEY            | Manifest + slip signing |
| SEMESTER_END_DATE          | e.g. 2026-12-20         |
| DEFAULT_CLEARANCE_DEADLINE | Fallback date           |
| BCRYPT_ROUNDS              | 12                      |
| RATE_LIMIT_MAX_ATTEMPTS    | 5                       |

### Rollback

Railway one-click rollback. Daily SQLite volume snapshots. Documented in docs/ROLLBACK.md.

## 10-Minute Demo Script

| Time | Section                         | Rubric                   | Points |
| ---- | ------------------------------- | ------------------------ | ------ |
| 0-1  | Intro & Architecture            | Design                   | 12     |
| 1-3  | Security demo (SQLi, RBAC, JWT) | Security                 | 20     |
| 3-5  | Hub API walkthrough             | Hub API                  | 15     |
| 5-7  | Data mapping & imports          | Data Mapping + Scripting | 23     |
| 7-8  | External APIs                   | External APIs            | 10     |
| 8-9  | Reports & testing               | Testing/Docs             | 10     |
| 9-10 | Live QR slip verification       | Demo                     | 10     |

## Contingencies

| Scenario        | Backup                         |
| --------------- | ------------------------------ |
| Railway down    | Localhost + pre-recorded video |
| Nager.Date down | Demonstrate fallback deadline  |
| Network failure | Screen recording on laptop     |
| Time runs short | Skip weather demo              |

## Pre-Demo Checklist

- Verify /api/health returns 200
- Run full import pipeline
- Test login for all three roles on mobile
- Clear browser cache on demo laptop
- Prepare backup screen recording
- Print QR code on physical card
