# Team Structure & Role Assignments

## Team A — Core Development (5 members)

| Role                              | Member | Responsibilities                  | Deliverables    |
| --------------------------------- | ------ | --------------------------------- | --------------- |
| Project Lead / Solution Architect | TBD    | Architecture, coordination, docs  | R3, R4, R18     |
| API Developer                     | TBD    | FastAPI endpoints, auth, deploy   | R5, R6, R7      |
| Data Integration Engineer         | TBD    | Import scripts, mapping, pipeline | R1, R2, R9, R10 |
| Security Engineer                 | TBD    | Auth, validation, audit, tests    | R11-R16         |
| Front-end / QA Developer          | TBD    | PWA screens, test suites          | R8, R17         |

## Team B — Extended Support (hats worn by Team A)

| Role                   | Worn By              | Responsibilities         |
| ---------------------- | -------------------- | ------------------------ |
| Database Administrator | Data Integration Eng | Schema, queries, backups |
| DevOps / Deployment    | API Developer        | Railway, Docker, CI/CD   |
| Technical Writer       | Project Lead         | README, WBS, docs        |
| UI/UX Designer         | Front-end / QA Dev   | Wireframes, layout, a11y |
| Data Analyst           | Data Integration Eng | Reports, reject analysis |

## Implementation Assignments

| Component            | Primary               | Support              |
| -------------------- | --------------------- | -------------------- |
| FastAPI app + auth   | API Dev               | Security Eng         |
| Import scripts S1-S6 | Data Integration Eng  | DBA                  |
| PWA front-end        | Front-end / QA Dev    | UI/UX                |
| Security layer       | Security Eng          | API Dev              |
| QA test suites       | Front-end / QA Dev    | Security Eng         |
| Deployment pipeline  | API Dev (DevOps)      | Data Integration Eng |
| Documentation        | Project Lead (Writer) | All                  |

## Timeline

| Week | Milestone         | Focus                       |
| ---- | ----------------- | --------------------------- |
| 14   | Proposal & design | All docs complete           |
| 15   | Core development  | API, auth, imports, PWA     |
| 16   | Integration       | External APIs, pipeline, QR |
| 17   | Testing & polish  | QA, security audit, dry run |
| 18   | Final demo        | Live presentation           |
