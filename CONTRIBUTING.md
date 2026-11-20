# Contributing — DNSC e-Clearance Hub Workflow

## Workflow Standard: Trunk-Based Development

We commit directly to the `main` branch to ensure rapid integration across all five project roles. To maintain complete audit discipline for external evaluators, all commits must strictly follow the Conventional Commits specification.

## Commit Conventions

Format: `<type>(<scope>): <short description>`

Types:
- `feat`: New feature or deliverable (e.g., `feat(security): implement Pydantic v2 schemas`)
- `fix`: Bug fixes (e.g., `fix(api): correct role authorization check`)
- `docs`: Documentation updates (e.g., `docs: update system architecture diagram`)
- `chore`: Infrastructure, dependencies, or cleanup (e.g., `chore(devops): update requirements.txt`)

## Role Assignments & Commit Scopes

| Role | Primary Scopes | Key Files Owned |
| ---- | -------------- | --------------- |
| Project Lead / Architect | `docs`, `release` | `README.md`, `TRACEABILITY.md`, `docs/*.md` |
| Security Engineer | `feat(security)`, `fix(security)` | `app/models/`, `app/security.py` |
| Data Integration Engineer | `feat(data)`, `feat(scripts)` | `app/database.py`, `scripts/` |
| API Developer (DevOps) | `feat(api)`, `chore(devops)` | `app/main.py`, `app/routers/`, `requirements.txt` |
| Front-end / QA Developer | `feat(ui)`, `test(qa)` | `static/`, `tests/` |

## Direct Push Etiquette

1. Always pull latest before starting work: `git pull origin main`
2. Test code locally before staging: `pytest tests/ -v`
3. Stage specific files only (never `git add .` blindly): `git add app/security.py`
4. Verify staged files before committing: `git diff --cached --stat`
5. Commit with appropriate role prefix and push: `git push origin main`
