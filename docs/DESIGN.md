# Solution Design Document (R3, R4)

## Problem Statement

DNSC students undergo a manual, paper-based clearance process requiring physical visits to each campus office (Library, Accounting, Registrar, Student Affairs, Laboratory). This process is slow, error-prone, and lacks transparency.

## Solution

A centralized web-based clearance hub that integrates data from all four offices into a single system, computes clearance status automatically, and issues cryptographically signed QR slips.

## Stakeholders

| Stakeholder | System Role |
|---|---|
| Students | View status, generate QR slips |
| Office Staff | Manage holds for assigned office |
| Registrar | View reports, export data |
| Admin / IT | Run imports, manage users, audit |

## Requirements Coverage

| Req | Description | Module | Status |
|---|---|---|---|
| R1 | Automation scripts | M1 | Designed |
| R2 | Bash orchestration | M1 | Designed |
| R3 | Solution design | M1-M4 | This document |
| R4 | Architecture diagram | M3 | See below |
| R5 | Registrar API integration | M3 | Designed |
| R6 | External API (Nager.Date, Open-Meteo) | M3 | Designed |
| R7 | Hub API specification | M3 | Designed |
| R8 | Front-end wireframes | M3 | Designed |
| R9 | Data mapping specification | M4 | Designed |
| R10 | Report export (CSV/JSON/XML) | M4 | Designed |
| R11-R16 | Security architecture | M4 | Designed |
| R17 | QA test plan | M1-M4 | Designed |
| R18 | Demo and deployment plan | M1-M4 | Designed |

## Technology Selection

| Layer | Choice | Justification |
|---|---|---|
| Language | Python 3.11 | Course requirement, starter kit |
| Framework | FastAPI | Auto docs, async, Pydantic |
| Database | SQLite | Course recommendation, <500 students |
| Hosting | Railway | Auto HTTPS, Python support |
| Front-end | Vanilla JS PWA | No build step, mobile-first |
| Auth | JWT + bcrypt | Stateless, secure |

## Architecture

[Clients: Student PWA / Staff PWA / Admin PWA / QR Scan]
|
v
[FastAPI Hub on Railway (HTTPS)]
|-- /api/auth/*
|-- /api/clearance/*
|-- /api/holdings/*
|-- /api/reports/*
|-- /api/health
|
+-- [SQLite Database]
+-- [Automation Scripts S1-S6]
+-- [External APIs: Registrar Mock, Nager.Date, Open-Meteo]


## Feasibility

- **Technical:** All components use course-taught technologies. Starter kit provides mock data and APIs.
- **Timeline:** 5 weeks (Weeks 14-18) with parallel team development.
- **Budget:** Railway free tier, all APIs free, no paid services required.

## Digital Transformation Impact

Replaces a multi-day paper process with a real-time digital system. Students check clearance from their phones. Staff coordinate across offices. The registrar has instant visibility into completion rates.

---