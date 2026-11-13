# Requirements Traceability Matrix

All 18 requirements mapped to specification documents, sections, and commits.

| Req | Description                            | Module | Document         | Section                                  | Commit  |
| --- | -------------------------------------- | ------ | ---------------- | ---------------------------------------- | ------- |
| R1  | Automation scripts                     | M1     | AUTOMATION.md    | Script Inventory, S1-S6                  | db7e136 |
| R2  | Bash orchestration                     | M1     | AUTOMATION.md    | S5 run_all_imports.sh                    | db7e136 |
| R3  | Solution design                        | M1-M4  | DESIGN.md        | Problem Statement, Solution, Feasibility | a6503ea |
| R4a | Architecture diagram                   | M3     | DESIGN.md        | Architecture                             | a6503ea |
| R4b | Deployment plan                        | M3     | DEMO.md          | Deployment                               | db16738 |
| R5  | Registrar API integration              | M3     | EXTERNAL_APIS.md | Registrar Mock API                       | 7e843e6 |
| R6  | External APIs (Nager.Date, Open-Meteo) | M3     | EXTERNAL_APIS.md | Nager.Date, Open-Meteo                   | 7e843e6 |
| R7  | Hub API specification                  | M3     | API_SPEC.md      | Endpoints 1-10                           | 78b19e1 |
| R8  | Front-end wireframes                   | M3     | WIREFRAMES.md    | Screen Inventory, Navigation             | 19b620e |
| R9  | Data mapping specification             | M4     | DATA_MAPPING.md  | Common Schema, Sources 1-4               | 383e0d7 |
| R10 | Report export (CSV/JSON/XML)           | M4     | DATA_MAPPING.md  | Report Export                            | 383e0d7 |
| R11 | Authentication (bcrypt + JWT)          | M4     | SECURITY.md      | Authentication Flow                      | 6d988e4 |
| R12 | Authorization (RBAC)                   | M4     | SECURITY.md      | RBAC Matrix                              | 6d988e4 |
| R13 | Input validation (Pydantic + SQL)      | M4     | SECURITY.md      | Security Controls                        | 6d988e4 |
| R14 | Manifest verification (HMAC)           | M4     | SECURITY.md      | Security Controls                        | 6d988e4 |
| R15 | Slip signing + ID masking              | M4     | SECURITY.md      | Security Controls                        | 6d988e4 |
| R16 | Audit logging + rate limiting          | M4     | SECURITY.md      | Audit Log Schema                         | 6d988e4 |
| R17 | QA test plan                           | M1-M4  | WIREFRAMES.md    | QA Test Plan Summary                     | 19b620e |
| R18 | Demo script                            | M1-M4  | DEMO.md          | 10-Minute Demo Script                    | db16738 |

## Notes

- R4 is split: R4a (architecture) in DESIGN.md, R4b (deployment) in DEMO.md
- Commit hashes reference the final state after all rebases
- All requirements designed and specified as of Week 14 milestone
- Implementation begins Week 15 against these frozen specifications
