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

Responses omit database IDs, publication flags, sort order, timestamps, and admin-only fields. Product images are optional. When present, the API returns their absolute media URL and the admin-entered alt text; when missing, `image` is `null`. The public frontend falls back gracefully if an image URL cannot be loaded.

Products and categories are managed through the authenticated Django Admin, not public write endpoints. Product image uploads accept validated JPEG/JPG, PNG, or WebP content; no public upload endpoint exists.

Phase 6 does not change the API or data schema. Owner content intake is maintained separately in the [product preparation guide](./PRODUCT_CONTENT_PREPARATION.md); optional grade, origin, processing, packaging, MOQ, documentation and certification fields in that template are not stored or exposed by the API.

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

There are no public admin API endpoints or buyer accounts. Authenticated Django admin is the staff interface for catalogue maintenance and enquiry triage. Staff can view, search, filter, update status, and add internal notes; public API responses contain only the opaque receipt reference and generic confirmation, never notes or enquiry details. Use least privilege, secure session settings, CSRF protection, strong unique staff credentials, and deployment-level access controls. The separate Phase 7 operations API below is private and limited to the documented farm/inventory collections; do not broaden its scope or expose it publicly without an approved authorization design.

## Protected farm and inventory operations API

Phase 7 adds private collection endpoints under `/api/v1/operations/`. These are not public catalogue endpoints and must only be called by staff-authorized tools:

| Route | Methods | Django model permission |
|---|---|---|
| `/api/v1/operations/farms/` | `GET`, `POST` | `view_farm`, `add_farm` |
| `/api/v1/operations/crop-seasons/` | `GET`, `POST` | `view_cropseason`, `add_cropseason` |
| `/api/v1/operations/harvests/` | `GET`, `POST` | `view_harvest`, `add_harvest` |
| `/api/v1/operations/batches/` | `GET`, `POST` | `view_productionbatch`, `add_productionbatch` |
| `/api/v1/operations/processing-records/` | `GET`, `POST` | `view_processingrecord`, `add_processingrecord` |
| `/api/v1/operations/inventory-movements/` | `GET`, `POST` | `view_inventorymovement`, `add_inventorymovement` |

Every request also requires an authenticated Django staff user. Session authentication is used; unsafe requests require Django CSRF protection. Inventory correction movement types additionally require `approve_inventory_correction`. No HTTP Basic authentication, anonymous reads, public farm data, detail routes, update methods, or delete methods are provided. Admin is the interface for editable farm/season/harvest/batch metadata; processing and inventory records are immutable after creation.

Collection responses use the standard paginated object (`count`, `next`, `previous`, `results`) with 25 records per page. `POST` creates one record and returns it with `201 Created`. Validation errors return `400` as `{ "errors": { "<field>": ["..."] } }`; missing staff authentication or model permissions returns `403` (or `401` when the authentication layer provides a challenge); unsupported methods return `405`. Related records are submitted by their unique reference string, e.g. `farm_reference`, `crop_season_reference`, `harvest_reference`, or `batch_reference`. Internal notes and supporting document references are visible only to authorized staff.

The batch endpoint returns `crop_season_reference`, `farm_reference`, and current `available_quantity_kg` so the harvest lineage and stock are explicit. The inventory movement list returns immutable event data; query the batch collection for its current availability. Product and enquiry public contracts are unchanged.

### Operation payloads

- Farm: `reference`, `name`, `location`, optional paired `area`/`area_unit` (`acre` or `hectare`), `description`, `internal_notes`, `is_active`.
- Crop season: `reference`, `farm_reference`, `crop_name`, optional `planting_date` and `expected_harvest_date`, `status`, `internal_notes`.
- Harvest: `reference`, `crop_season_reference`, `harvest_date`, positive `quantity`, `quantity_unit` (`kg` or `metric_tonne`), `notes`.
- Production batch: `reference`, `harvest_reference`, `product_name`, `batch_date`, positive `initial_quantity`, `quantity_unit`, `status`, `internal_notes`. Creation also writes the first production receipt atomically.
- Processing record: `batch_reference`, `activity`, `activity_date`, optional paired input/output quantity and unit, `description`, `supporting_document_references`, `internal_notes`.
- Inventory movement: optional server-generated `reference`, `batch_reference`, `movement_type`, positive `quantity`, `quantity_unit`, `movement_date`, required `reason`, `internal_notes`. Quantity is positive; movement type expresses direction.

Inventory types are production receipt, processing increase/decrease, reservation, reservation release, dispatch, and approved correction increase/decrease. Batch creation automatically records the sole initial production receipt. See [database inventory rules](./DATABASE.md#inventory-ledger-and-calculation) for balance calculation, reservation, dispatch, chronology, and correction semantics.

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
