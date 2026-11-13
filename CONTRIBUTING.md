# Contributing — Week 15 Workflow

## Branch Protection

The `main` branch is protected. All changes require a pull request.

**Settings (GitHub → Settings → Branches → Add rule for `main`):**

- Require a pull request before merging
- Require approvals: 1
- Require linear history
- Do not allow bypassing the above settings

At PR merge time, always choose **"Rebase and merge"**.

## Branch Naming

| Pattern | Example              | Use                                |
| ------- | -------------------- | ---------------------------------- |
| feat/   | feat/auth-login      | New feature                        |
| fix/    | fix/xml-parser       | Bug fix                            |
| docs/   | docs/update-api-spec | Documentation only (self-merge OK) |

## Workflow

1. **Sync before branching:**
   ```bash
   git checkout main
   git pull --rebase origin main
   git checkout -b feat/your-feature
   ```
2. **Commit in small units:**
   ```bash
   git add app/auth.py
   git commit -m "Add bcrypt password hashing"

```

```
