# Contributing to SPICEORA

Thank you for contributing to SPICEORA. As a premium B2B Indian spice-export business platform, this repository maintains high standards of data integrity, factual truthfulness, and code quality.

---

## 1. Development Environment Setup

Follow the local setup instructions in [README.md](README.md):

* **Backend Requirements:** Python 3.12+, virtual environment under `backend/.venv/`, dependencies installed from `backend/requirements.txt`.
* **Frontend Requirements:** Node.js 20+, npm 10+, dependencies installed from `frontend/package.json`.
* **Database & Secrets:** Never commit `.env` or credentials. Use `.env.example` as a template. Note that on Windows with MySQL 8 `caching_sha2_password`, `DB_HOST=localhost` must be used.

---

## 2. Contribution & Branch Workflow

1. Always branch off the latest verified `main` branch:
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b feat/phase-X-description
   ```
2. Keep changes scoped strictly to the approved phase or issue. Do not bundle unrelated refactoring, dependency changes, or stylistic churn.
3. Commercial, legal, or product claims MUST be backed by owner-approved documentation before any public commit.

---

## 3. Pre-Pull Request Verification Checklist

Every pull request must pass the complete local test suite and static checks prior to requesting review:

### A. Backend Isolated Suite & Schema Drift
Run from `backend/`:
```powershell
# 1. System check
python manage.py check

# 2. Check for migration drift (models must be 100% in sync with migrations)
python manage.py makemigrations --check --dry-run --settings=config.test_settings

# 3. Run complete isolated-database test suite (99 API tests + Settings Security)
python manage.py test --settings=config.test_settings
```

### B. Frontend Verification (Tests, Lint, Build)
Run from `frontend/` (or from root using `--prefix frontend`):
```powershell
# 1. Run Vitest suite (13 unit and integration tests)
npm run test:run

# 2. Run Oxlint static linter
npm run lint

# 3. Run Vite production build (must compile without bundling errors)
npm run build
```

---

## 4. Git Diff Review & Security Rules

Prior to staging or requesting review, perform a security and diff inspection:

1. **Check for Whitespace and Formatting Defects:**
   ```powershell
   git diff --check
   ```
2. **Strict Credential Protection:**
   * **Never commit `.env` files, API keys, Google App Passwords, or database passwords.**
   * **Never commit database dumps, backups, or SQL scripts (`*.sql`).**
   * If a local reset script or password was ever exposed in an uncommitted local file (e.g. `mysql_reset.sql`), follow secure credential handling and rotate the active password immediately.
   * Verify with `git status` that `.env` and all sensitive files remain untracked.
3. **Database Safeguards:**
   * Never execute `flush`, `reset_db`, or destructive SQL against any shared or production database.
   * Migrations must be additive and backward-compatible. Deleting or modifying existing database columns requires explicit review.
   * Product and category records must never be deleted if referenced by existing enquiries or operational records.
4. **Git Identity:**
   * Commits must preserve the verified repository author:
     ```powershell
     git config user.name "Maahin"
     git config user.email "maahinsuthar4565@gmail.com"
     ```

---

## 5. Commit Message Convention

Format all commit messages consistently with project history:
```text
Phase X: <concise summary of implemented milestone>
```
*Examples:*
* `Phase 11: complete farm and crop season management`
* `Phase 12: complete harvest management`
* `docs: update core documentation for Phase 13.2`

---

## 6. Release & Approval Boundary

* **Read-Only Inspection / Local Development:** Developers and assistants may inspect code, run tests, and draft documentation.
* **Release Approval:** Separate, explicit approval from Maahin is required before staging, committing, pushing to `origin/main`, or deploying to any environment.
