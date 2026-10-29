# API Plan

## Existing endpoint

The only application API currently implemented is `GET /api/health/`, returning `{"status":"ok"}`. It indicates Django liveness only; it is not database readiness. All routes below are **Phase 1 proposals**, not implemented endpoints.

The Phase 2 homepage links to a visible enquiry placeholder only. It has no form, network submission, or customer data collection.

## Proposed convention

Use `/api/v1/` for the first business API version. JSON requests/responses use UTF-8. Public responses expose only approved, active catalog content and never include internal notes, private enquiry details, database identifiers intended for staff, or unpublished facts.

### Public read endpoints

| Method and path | Responsibility | Response |
|---|---|---|
| `GET /api/v1/categories/` | List active categories in editorial order | `[{id, slug, name}]` |
| `GET /api/v1/products/` | List active products; optional `category` slug filter | Paginated `{results: [{slug, name, category, summary, image?, ...}]}` |
| `GET /api/v1/products/{slug}/` | Read a single active product | `{slug, name, category, summary, description, approved_content...}` |

Do not return products or category labels merely because they exist in the database; require an explicit published/active state. Add pagination only as the catalogue grows; the response shape should remain stable.

### Public write endpoint

`POST /api/v1/enquiries/` accepts an anonymous contact, export enquiry, or quotation request. Proposed request:

```json
{
  "intent": "quotation",
  "contact_name": "Buyer contact",
  "email": "buyer@example.com",
  "company_name": "Buyer company",
  "country": "Buyer country",
  "phone": "",
  "message": "Please share information about the requested products.",
  "items": [
    {"product_slug": "approved-product-slug", "quantity_note": ""}
  ],
  "privacy_notice_version": "published-version"
}
```

Example values illustrate the contract only; do not use sample content as real customer data. Fields, requiredness, privacy acknowledgement, and whether multiple items are allowed require owner/legal confirmation.

Success response: `201 Created`, `{ "reference": "opaque-reference", "message": "Your enquiry has been received." }`. Do not promise a response time. Validation errors: `400 Bad Request`, `{ "errors": { "email": ["Enter a valid email address."] } }`. Rate limit: `429 Too Many Requests`, generic retry guidance. Unexpected failures: generic `500` message with no exception details.

The server must validate all values and product slugs, reject unpublished/unknown products where product selection is required, apply abuse controls, and persist the enquiry and items atomically. Do not return or expose another buyer’s enquiry by reference.

## Protected administrative operations

There are no planned public admin API endpoints or buyer accounts for launch. Use the Django admin interface for authenticated staff catalog maintenance and enquiry triage, with least privilege, secure session settings, CSRF protection, strong unique staff credentials, and deployment-level access controls. Add a dedicated admin API only when a justified integration requires it and its authentication/authorization model is approved.

## Validation and error handling

- Enforce required fields, allow-listed `intent`, maximum lengths, valid email syntax, and allowed active product slugs on the server.
- Normalize/trim input where appropriate; do not rely on browser validation.
- Return stable machine-readable field errors; never return SQL, tracebacks, secrets, or internal notes.
- Log a correlation ID and operational error details server-side with PII redaction.
- Avoid logging request bodies, email, phone, message, cookies, or authorization headers.
- Apply endpoint-level and edge-level abuse controls; exact thresholds need launch traffic and operations input.

## CORS, CSRF and authentication

Prefer a same-origin production deployment. If origins are separated, allow only exact approved frontend origins. Public anonymous JSON submission should not use browser credentials/cookies. Admin remains session-authenticated and CSRF-protected; do not disable CSRF globally. Configure `CSRF_TRUSTED_ORIGINS` only for actual HTTPS admin origins if required. The current CORS configuration is development foundation, not a complete production security policy.

See [application architecture](./ARCHITECTURE.md) and [security](./SECURITY.md).
