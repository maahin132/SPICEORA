# Testing Plan

## Current foundation checks

From `backend/` with the virtual environment active:

```powershell
python manage.py check
python manage.py check --database default
python manage.py migrate --check
python manage.py test --settings=config.test_settings
```

The system and database checks use the local MySQL database configured by `.env`. The API tests use the in-memory SQLite test settings to keep test data isolated and avoid creating a separate MySQL test database; all test data is discarded. The suite covers public catalogue listing/filtering, enquiry submission/validation, quantity rules, product/category visibility, response field exposure, rate limiting, admin status and note management, and image alternative-text validation.

From `frontend/`:

```powershell
npm run lint
npm run build
```

There is no frontend component/interaction test runner configured. Browser smoke checks should cover the home page, catalogue, enquiry form, and product-specific enquiry preselection at desktop and mobile widths; form validation, pending/success/error states; product list/filter/detail navigation; loading/empty/error/not-found states; image fallback; and mobile menu keyboard behavior.

## Proposed tests before public launch

### Backend

- Catalog query/serializer tests: active-only visibility, category filtering, stable slug lookup, unpublished/missing product handling.
- Enquiry serializer/service tests: each intent, required/optional fields, bounds/format checks, rejected unknown/inactive products, multi-item behavior if approved, and transactional rollback on failed item insert.
- API tests: success/status/error contract, anonymous access limited to public operations, no enquiry read/list exposure, and no leakage of internal fields.
- Security/abuse tests: configured rate limiting, oversized body rejection, generic server errors, logging redaction, CSRF/session policy, and exact-origin CORS behavior.
- Admin tests: permissions for catalog and enquiry status changes; unauthorized staff cannot read/update enquiries.
- MySQL integration tests on the supported MySQL version and collation; migration forward test and backup/restore rehearsal.

### Frontend

- Route and not-found behavior; loading, empty, and error states for catalogue content.
- Product category navigation and product-to-enquiry prefill.
- Accessible form labels, keyboard use, focus/error announcements, validation, pending/success/failure states.
- Responsive viewport tests, image alternatives/captions, contrast and reduced-motion behavior.
- API contract tests, with no customer PII in client logs or analytics.

### Release checks

Run dependency/security scanners and static checks, review secrets/artifacts, test production configuration with `DEBUG=false`, and verify HTTPS, cookies, headers, CORS/CSRF, rate limits, logs, retention and restores in the deployed environment. No planned feature should be described as tested until its tests exist and pass.

The product catalogue, public read APIs, and enquiry submission are implemented. Before launch, add frontend automated interaction tests and execute production deployment/security checks, including rate-limit behavior with the configured shared cache and edge controls.
