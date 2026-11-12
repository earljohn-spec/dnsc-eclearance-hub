# DNSC e-Clearance Hub

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org/)
[![Railway](https://img.shields.io/badge/Railway-Deployed-0B0D0E?style=flat-square&logo=railway)](https://railway.app/)
[![Institution](https://img.shields.io/badge/DNSC%20Panabo-IT312%20Track%20A-amber?style=flat-square)]()

Centralized clearance hub integrating Library (XML), Accounting (CSV), Registrar (JSON API), and Student Affairs (manual) data into a secure FastAPI platform with signed QR slip verification.

---

## Tech Stack

Python 3.11 · FastAPI · SQLite · Railway · JWT + bcrypt · HMAC-SHA256 · PWA (vanilla JS) · pytest

---

## Team

| Role | Key Deliverables |
|---|---|
| Project Lead / Architect | R3, R4, R18 |
| API Developer | R5, R6, R7 |
| Data Integration Engineer | R1, R2, R9, R10 |
| Security Engineer | R11–R16 |
| Front-end / QA Developer | R8, R17 |

---

## API Endpoints

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| POST | `/api/auth/login` | None | All |
| GET | `/api/clearance/me` | JWT | Student |
| GET | `/api/clearance/student/{id}` | JWT | Staff/Admin |
| GET | `/api/clearance/deadline` | JWT | All |
| POST | `/api/clearance/slip` | JWT | Student |
| GET | `/api/clearance/verify/{token}` | None | Public |
| PUT | `/api/holdings/{id}` | JWT | Staff |
| POST | `/api/student-affairs/records` | JWT | Staff |
| GET | `/api/reports/registrar?format=` | JWT | Admin |
| GET | `/api/health` | None | Public |

Full spec: `docs/API_SPEC.md`

---

## Automation Pipeline

S1 verify_manifests.py → S2 import_library.py → S3 import_accounting.py
→ S4 sync_registrar.py → S6 compute_clearance.py


Orchestrated by `S5 run_all_imports.sh` (cron 02:00 or admin trigger).
Details: `docs/AUTOMATION.md`

---

## External APIs

| API | Purpose | Fallback |
|---|---|---|
| Registrar Mock (starter kit) | Student enrollment data | Previous cached sync |
| Nager.Date (public) | PH holidays → deadline | Hardcoded default date |
| Open-Meteo (public) | Campus weather widget | Widget hidden |

---

## Security Summary

bcrypt (12 rounds) · JWT (1hr) · RBAC (student/staff/admin) · Pydantic validation · parameterized SQL · HMAC-SHA256 manifests & slip signing · append-only audit log · rate limiting (5/15min) · HTTPS

Full plan: `docs/SECURITY.md`

---

## Timeline

| Week | Milestone |
|---|---|
| 14 | Proposal & design docs |
| 15 | Core API, auth, imports, PWA |
| 16 | External APIs, pipeline, QR slips |
| 17 | QA, security audit, demo dry run |
| 18 | Final demo (30 external raters) |

---

## Getting Started

```bash
git clone https://github.com/earljohn-spec/dnsc-clearance-hub.git
cd dnsc-clearance-hub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit with your keys
python -m scripts.init_db
python registrar_mock_api.py  # terminal 1
uvicorn app.main:app --reload # terminal 2
python -m pytest tests/ -v
```

---

## Repo Structure

app/          FastAPI application
scripts/      S1–S6 automation pipeline
static/       PWA front-end assets
templates/    HTML templates
tests/        pytest suites (69 cases)

---
data/         Starter kit files (XML, CSV, JSON)
migrations/   SQL schema
docs/         Full specifications
