# API Plan

## Implemented public endpoints

`GET /api/health/` returns `{"status":"ok"}` as a liveness check; it is not database readiness.

The anonymous catalogue is implemented at `/api/v1/`. Catalogue reads expose only published products in active categories; the enquiry endpoint supports public creation only.

### `GET /api/v1/categories/`

Returns all active owner-provided categories, sorted by editorial order. A category label does not assert product availability:

```json
[{"slug":"cumin","name":"Cumin"}]
```

The initial migration creates the six owner-provided category labels, so this endpoint returns those active labels even when no product is published.

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

## `POST /api/v1/enquiries/`

Publicly submits one export enquiry. The request must identify exactly one active `category_slug` or one published `product_slug`; the server derives a product's category.

```json
{
  "full_name": "Buyer contact",
  "company_name": "Buyer company",
  "email": "buyer@example.com",
  "phone": "",
  "country": "Buyer country",
  "category_slug": "cumin",
  "quantity": "500",
  "quantity_unit": "kg",
  "message": "Please share information about this category."
}
```

`full_name`, `email`, `country`, one interest selector, a positive estimated quantity, and its unit are required. Company, phone, and message are optional. Supported units are `kg` and `metric_tonne`; decimal quantity must have at most three decimal places. Product selection accepts only published products in active categories. Category selection accepts any active owner-provided category, including categories with no published products.

Success response: `201 Created`, `{ "reference": "<opaque-uuid>", "message": "Your enquiry has been received." }`. The reference is confirmation only; there is no public enquiry lookup endpoint (`GET` returns `405`). Validation errors return `400 Bad Request`, `{ "errors": { "email": ["Enter a valid email address."] } }`. Excess submissions return `429 Too Many Requests` with generic retry guidance. Production must run with `DEBUG=false`; no custom error handler/correlation logging has been added.

The server validates all values, rejects unknown request fields and invalid/inactive/unpublished interest selectors, applies an IP-based limit of five requests per hour, and persists the enquiry in one database insert. No email notification is configured or implied. Do not promise a response time or return another buyer's enquiry by reference.

## Protected administrative operations

There are no public admin API endpoints or buyer accounts. Authenticated Django admin is the staff interface for catalogue maintenance and enquiry triage. Staff can view, search, filter, update status, and add internal notes; public API responses contain only the opaque receipt reference and generic confirmation, never notes or enquiry details. Use least privilege, secure session settings, CSRF protection, strong unique staff credentials, and deployment-level access controls. Add a dedicated admin API only when a justified integration requires it and its authentication/authorization model is approved.

## Validation and error handling

- Enforce required fields, maximum lengths, valid email syntax, positive bounded quantity, quantity/unit pairing, and exactly one active category or published product on the server.
- Normalize/trim input where appropriate; do not rely on browser validation.
- Return stable machine-readable field errors; never return SQL, tracebacks, secrets, or internal notes.
- Production should add a correlation ID and operational error logging with PII redaction; custom correlation logging is not currently implemented.
- Avoid logging request bodies, email, phone, message, cookies, or authorization headers.
- The endpoint currently uses a five-per-hour IP-based Django REST Framework throttle. The default local-memory cache is not shared across workers or hosts; production requires a shared cache and edge-level controls, proxy/IP configuration review, and traffic-based tuning.

## CORS, CSRF and authentication

Prefer a same-origin production deployment. If origins are separated, allow only exact approved frontend origins. Public anonymous JSON submission does not send browser credentials/cookies. Admin remains session-authenticated and CSRF-protected; do not disable CSRF globally. Configure `CSRF_TRUSTED_ORIGINS` only for actual HTTPS admin origins if required. The current CORS configuration is development foundation, not a complete production security policy.

See [application architecture](./ARCHITECTURE.md) and [security](./SECURITY.md).
