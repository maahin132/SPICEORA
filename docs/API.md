# API Plan

## Implemented read endpoints

`GET /api/health/` returns `{"status":"ok"}` as a liveness check; it is not database readiness.

The anonymous, read-only catalogue is implemented at `/api/v1/`. Only published products in active categories are exposed.

### `GET /api/v1/categories/`

Returns the active categories that currently contain published products, sorted by editorial order:

```json
[{"slug":"cumin","name":"Cumin"}]
```

The initial migration creates the six owner-provided category labels, but no products, so this endpoint currently returns an empty list.

### `GET /api/v1/products/`

Returns a paginated object with `count`, `next`, `previous`, and `results`:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [{
    "slug": "owner-approved-product-slug",
    "name": "Owner-approved product name",
    "category": {"slug": "cumin", "name": "Cumin"},
    "summary": "Owner-approved concise description.",
    "image": null,
    "image_alt": ""
  }]
}
```

The page size is 12. `?page=<positive integer>` selects a page. Optional `?category=<active-category-slug>` filters results. Unknown or repeated query parameters, blank/invalid page values, and blank or unknown/inactive category slugs return `400` with an `errors` object. An out-of-range page returns `404`.

### `GET /api/v1/products/{slug}/`

Returns the public product fields directly: `slug`, `name`, `category`, `summary`, `image`, `image_alt`, and `description`. Missing, unpublished, and products whose category is inactive all return `404` without revealing publication state. Image URLs are absolute URLs when a file is present; absent images return `null`.

Responses omit database IDs, publication flags, sort order, timestamps, and admin-only fields.

## Future public write endpoint (not implemented)

`POST /api/v1/enquiries/` is still a proposal for a later approved phase. It is not available, and the website does not collect or submit buyer data. Proposed request:

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
