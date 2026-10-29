# Testing Plan

## Current foundation checks

From `backend/` with the virtual environment active:

```powershell
python manage.py check
python manage.py check --database default
python manage.py migrate --check
python manage.py test
```

The database checks require a running MySQL server and valid local `.env` credentials. The current automated backend suite contains a health endpoint test; it does not validate planned catalog/enquiry behavior.

From `frontend/`:

```powershell
npm run lint
npm run build
```

There is no frontend component/interaction test runner configured. Phase 2 homepage verification therefore also uses a browser smoke test at desktop and mobile widths: verify the primary and section links, mobile menu open/close, Escape handling and focus restoration, local image loading/fallback, responsive layout, and that the enquiry placeholder does not claim to submit.

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

The product catalog, backend APIs, and enquiry submission remain unimplemented; their tests belong to a later approved phase.
