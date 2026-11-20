# Contributing Guidelines - DNSC e-Clearance Hub

## Workflow Strategy
This project strictly adheres to single-branch Trunk-Based Development directly on `main`. All feature additions, bug fixes, and documentation updates are committed directly to `main` with clear, descriptive commit messages mapping to the 5 IT field roles.

## Role Attribution Matrix
| Role Scope | Designated Git Author Name | Designated Git Email |
| :--- | :--- | :--- |
| Project Lead / Architect | earljohn-spec | earljohnbplaza@gmail.com |
| Security Engineer | jeboysuganob15-create | jeboysuganob15@gmail.com |
| Data Integration Engineer | yorimendoza | mendozayori123@gmail.com |
| API Developer / DevOps | API Developer | api.devops@dnsc.edu.ph |
| Front-end / QA Developer | QA Front-end Engineer | qa.frontend@dnsc.edu.ph |

## Role Permissions Design (R14-R18)
- **Role-Based Authorization:** Departmental staff roles (`ADMIN`, `ACCOUNTING_STAFF`, `REGISTRAR_STAFF`, `LIBRARY_STAFF`, `STUDENT_AFFAIRS_STAFF`) are authorized to create, view, and clear holds across institutional systems.
- **Scope & Boundaries:** Authorization is role-based across all clearance source systems. Row-level hold ownership enforcement is handled at the institutional departmental interface layer.
