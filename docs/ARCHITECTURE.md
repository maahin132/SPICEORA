# Application Architecture

## Status and decision labels

- **Existing foundation:** verified in the repository after Phase 0.
- **Phase 1 proposal:** planned boundary or behavior; not implemented.
- **Owner confirmation required:** business, legal, or operational input needed before launch.

Phase 1 was documentation-only. Phase 2 implements a React homepage, shared header/footer and responsive design foundation. Phase 3 adds Django product/category models, staff admin management, a public catalogue API, and React catalogue/detail routes. Phase 4 adds public enquiry creation, an accessible React form with contextual product preselection, and staff enquiry triage in Django admin. Phase 5 improves product/category admin content workflows, protects enquiry-linked products from deletion, and validates product image uploads. Phase 6 prepares owner-verified catalogue content through a non-imported CSV template, improves empty-state enquiry navigation, and applies route-aware browser titles and descriptions without adding product fields or records. Phase 7 adds private farm-to-inventory records, immutable stock movements, Django Admin workflows, and paginated staff-only API collections. No notification provider or multi-item quote workflow is configured.

The frontend uses `SiteHeader`, `HomePage`, `ProductsPage`, `ProductDetailPage`, `EnquiryPage`, `ProductCard`, and `SiteFooter`, with `catalog.js` for API calls and `useCatalogRequest.js` for read/loading states. Shared design tokens and responsive states live in the Tailwind CSS v4 `@theme` block and semantic rules in `frontend/src/index.css`. The mobile navigation is a disclosure (not a modal): it exposes expanded state, closes on link selection or Escape, and returns focus to its toggle on Escape.

## Existing foundation

- `frontend/`: React JavaScript/JSX SPA built with Vite. Tailwind CSS is available for styling, React Router for route composition, and Lucide React for interface icons.
- `backend/`: Django + Django REST Framework project. Django loads local settings from root `.env`.
- MySQL: local development database configured through environment variables.
- Development data flow: Vite proxies `/api` and `/media` requests to Django. `/api/v1/categories/` exposes active category labels; product reads expose only published products in active categories. Product detail uses `/api/v1/products/{slug}/`.
- Product images are optional Django `ImageField` uploads. Admin uploads are restricted to matching JPG/JPEG, PNG, and WebP images no larger than 5 MiB, 8,000 px per side, or 40 megapixels; new files receive random UUID names. Development media is served by Django only when `DEBUG` is enabled. Production media storage/CDN configuration remains future deployment work.

### Phase 3 implementation boundaries

- Product categories and products are managed only through authenticated Django admin; catalogue APIs are read-only and `AllowAny`.
- Products default to unpublished. Responses do not include internal IDs, publication flags, sort ordering, or timestamps.
- The product list is page-number paginated (12 per page), optionally filtered by an active category slug. Unknown query parameters and invalid filters return structured 400 errors; unpublished/inactive detail slugs return 404.
- No products are preloaded. Category label rows come from the owner brief and do not claim inventory or availability.
- The frontend uses `VITE_API_BASE_URL` when set, otherwise `/api/v1`. Vite proxies `/api` and `/media` in development. No credential is exposed in Vite configuration.

### Phase 4 enquiry implementation boundaries

- `/enquiry/` sends JSON to `POST /api/v1/enquiries/` without browser credentials. Product detail passes a published product and category in the URL; category-only enquiries remain available for all active categories.
- The server validates names, email, country, interest, quantity/unit pairing and bounds, rejects unknown input keys, writes one enquiry record, and returns an opaque receipt reference. The public API has no read operation and never serializes internal notes or status.
- The database enforces a positive quantity/allowed-unit constraint and protects enquiry categories from deletion; optional product links are set null on product deletion while preserving a name snapshot.
- Django admin is the only enquiry read/update surface. Staff can search, filter by status/date/category, update status, and maintain internal notes.
- Django REST Framework applies five requests per hour per client IP using its configured cache. The default development cache is local-memory and not a production distributed abuse-control system.
- Email notification, multi-product line items, privacy notice/jurisdiction, retention/deletion policy, production shared-cache and edge rate limits remain unconfigured or require owner review.

### Phase 5 product content workflow

- Authorized staff use Django Admin to create, edit, search, filter, order, publish/unpublish and delete products and manage categories. Product lists include publication state, category, sort order, creation date and image preview.
- Product and category references are protected from deletion when used by products/enquiries. Enquiry-linked products cannot be deleted; unreferenced products use the standard admin confirmation flow.
- New image filenames are randomized; replacing/removing an image does not rewrite other stored image paths. Local development media uses `MEDIA_ROOT/products/`; production storage and delivery are not configured.
- The public API contract is unchanged: only published products in active categories are returned, optional images use absolute URLs, and unpublished or deleted product slugs return 404. The frontend keeps the existing visual system and missing-image fallback.
- A CSV content-intake template provides blank rows for the six existing category labels. It is not a fixture or import source. Browser titles and meta descriptions use confirmed page labels and the published product name/short summary only; no unknown product structured data or production canonical domain is asserted.
- Route metadata is updated client-side in the React SPA. The initial HTML has only generic SPICEORA metadata; server-side rendering/prerendering and production canonical URLs are not configured.

### Phase 7 farm-to-inventory operations

- Operational records follow `Farm → CropSeason → Harvest → ProductionBatch → ProcessingRecord / InventoryMovement`. Crop names are staff-entered, not seeded from the public product catalogue; no farm or production records are created by migrations.
- Django Admin is the interactive staff interface. Protected `/api/v1/operations/` collection routes require a staff session, per-model Django view/add permissions, and CSRF validation for writes. They are paginated and support list/create only; editing/deactivation/status changes use Django Admin, while processing and inventory events are append-only.
- New production batches must reference a harvest and allocate no more than its remaining harvest quantity. Batch creation atomically records the initial quantity as a production-receipt movement. Harvest and batch units support kilograms and metric tonnes with stock normalized to kilograms.
- Inventory is a movement ledger, not a mutable balance field. On-hand quantity changes with production receipt, processing increase/decrease, dispatch, and approved corrections. Reservations and releases alter reserved quantity; dispatch consumes reserved stock first. Available quantity is `on_hand_kg - reserved_kg`. Outflows/reservations are validated under a batch row lock; negative available or physical stock is rejected.
- A processing record is factual documentation only and does not automatically alter inventory; staff record any actual stock effect as a separate movement. No facility, method, certification, processing capability, or export readiness is implied.
- Farm/season/harvest/batch references are protected from deletion. Batch identity and source quantity, processing records, and inventory movements cannot be retrospectively rewritten; use a new movement for an approved correction.
- No custom React operations route was added: the public SPA has no staff login, session/CSRF handling, or authorization UX. Do not expose operational endpoints through public pages; a separate secure staff frontend requires an approved authentication design.

## Proposed production architecture

Prefer a same-origin public website deployment: serve the compiled React assets and `/api/` through one HTTPS origin, with Django behind a production application server and a managed MySQL instance. This simplifies browser security policy and avoids broad CORS. A separate frontend/API origin is possible only when the deployment owner approves it and exact origins are configured.

```text
Buyer browser
  ├─ React route/page components
  ├─ reusable presentation and form components
  └─ typed-by-convention JS API client
       └─ HTTPS /api/v1/* → Django REST Framework
                             ├─ public read serializers/views
                             ├─ public enquiry validation/service
                             ├─ protected Django admin
                             └─ MySQL
```

### Frontend component boundaries — proposal

- **App shell:** shared header, navigation, footer, route error/not-found states.
- **Route pages:** Home, Products catalogue, Product detail, Contact & export enquiry, and Privacy. Optional About and Export process pages should only be split out when verified content exists.
- **Product presentation:** category navigation, product list, product detail sections, image/caption, and contextual enquiry links. Product facts come from published API data, not hardcoded invented claims.
- **Enquiry flow:** validated form, selected-product summary, accessible field errors, pending state, success confirmation, and retry-safe failure state. Do not promise a response time unless approved.
- **API client:** one module for URL construction, JSON parsing, timeouts, and consistent error mapping. Components should not duplicate fetch/error logic.
- **Design primitives:** content width, spacing, typography, button, form field, notice, and image-caption patterns following the [design brief](./DESIGN_SYSTEM.md).

### Backend component boundaries — proposal

- **Catalog read API:** serializers expose only active, publishable categories and products.
- **Enquiry API:** one public create operation for a category or a single product interest; validation is server-side and one enquiry row is persisted atomically.
- **Admin:** Django admin for staff to maintain catalog records and triage enquiries. No public admin API or buyer accounts in launch scope.
- **Domain validation:** enforce field lengths, allowed enquiry type, product eligibility, and consistency on the server even when client-side validation exists.
- **Operational boundary:** email notifications, file uploads, CRM sync, and analytics are not assumed. Add them only after a real owner workflow and retention/security design are approved.

## Request and error flow

1. The page requests public catalogue data over same-origin `/api/v1/`.
2. The API returns only records marked active/published; empty catalogues have a clear editorial state rather than invented products.
3. The browser sends one enquiry for an active category or a published product, with required estimated quantity/unit and optional company, phone, and message context.
4. The server validates, rate-limits, persists atomically, and returns a non-sensitive reference/confirmation.
5. The UI shows field-level validation errors for correctable input; network/server failures receive a generic retry message and a correlation identifier when available. Never display stack traces, SQL, or internal exception text.

Use a consistent JSON error envelope and appropriate HTTP status codes. Distinguish invalid fields (400), rate limiting (429), missing public resources (404), and unexpected failures (500). Do not treat a failed notification as a failed database write without an explicit outbox/retry design.

## Configuration and deployment

Keep `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, database credentials, allowed origins, and any future rate limits in environment-specific secret/configuration stores. Never place secrets in frontend build variables, source control, or browser responses. Production requires HTTPS, a production WSGI/ASGI server, controlled migrations, static/media storage policy, backups, logs/alerts, restore tests, and a documented rollback plan. Hosting provider and topology require owner approval.

## Deferred choices

- Hosting provider, domain, DNS, CDN/WAF, storage and email delivery
- Whether content is managed in Django admin or a separate workflow
- Whether a separate API origin is necessary
- Product images/CMS, search, localization, and currency handling
- Enquiry notifications, retention schedule and operational response process

Related plans: [database](./DATABASE.md), [API](./API.md), [security](./SECURITY.md), and [deployment](./DEPLOYMENT.md).
