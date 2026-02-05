# Git Standards

## 1. Branch Strategy
We use a simplified Gitflow.

| Branch | Purpose | Merge Target |
|--------|---------|--------------|
| `main` | Production code. Stable. | - |
| `develop` | Integration branch. | `main` |
| `feature/*` | New features. | `develop` |
| `bugfix/*` | Non-critical bug fixes. | `develop` |
| `hotfix/*` | Critical production fixes. | `main` & `develop` |
| `release/*` | Release preparation. | `main` |

## 2. Naming Conventions (Jira)
Format: `<type>/<JIRA-ID>-<short-description>`

**Examples**:
- `feature/DATA-123-ingest-customers`
- `bugfix/ECRED-567-fix-dedup`
- `hotfix/DATA-345-prod-timeout`

## 3. Conventional Commits
Follow the Conventional Commits specification for commit messages.

| Type | Usage | Example |
|------|-------|---------|
| `feat` | New feature | `feat(DATA-123): add bronze processor` |
| `fix` | Bug fix | `fix(DATA-123): handle nulls in date` |
| `docs` | Documentation | `docs: update readme` |
| `refactor` | Code restructuring | `refactor: move utils to shared` |
| `chore` | Maintenance | `chore: update dependencies` |

## 4. Workflow Commands
```bash
# Start Feature
git checkout -b feature/DATA-123-desc

# Commit
git add .
git commit -m "feat(DATA-123): description"

# Push
git push origin feature/DATA-123-desc
```
