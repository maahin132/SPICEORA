# Application Architecture

## Status and decision labels

- **Existing foundation:** verified in the repository after Phase 0.
- **Phase 1 proposal:** planned boundary or behavior; not implemented.
- **Owner confirmation required:** business, legal, or operational input needed before launch.

Phase 1 was documentation-only. Phase 2 implements a React homepage, shared header/footer and responsive design foundation. The current backend still has Django admin and `GET /api/health/` only; no product/contact/enquiry API or database entities exist. The enquiry section is an honest configuration placeholder and does not accept or send submissions.

The current homepage is built from `SiteHeader`, `HomePage`, `SiteFooter`, and local editorial image/section presentation components. Shared design tokens and responsive states live in the Tailwind CSS v4 `@theme` block and semantic rules in `frontend/src/index.css`. The mobile navigation is a disclosure (not a modal): it exposes expanded state, closes on link selection or Escape, and returns focus to its toggle on Escape.

## Existing foundation

- `frontend/`: React JavaScript/JSX SPA built with Vite. Tailwind CSS is available for styling, React Router for route composition, and Lucide React for interface icons.
- `backend/`: Django + Django REST Framework project. Django loads local settings from root `.env`.
- MySQL: local development database configured through environment variables.
- Development data flow: Vite proxies `/api` requests to Django. No product or enquiry API currently exists.

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
- **Enquiry API:** one public create operation for contact, export enquiries, and quotation requests; validate and persist the enquiry plus optional selected products in a transaction.
- **Admin:** Django admin for staff to maintain catalog records and triage enquiries. No public admin API or buyer accounts in launch scope.
- **Domain validation:** enforce field lengths, allowed enquiry type, product eligibility, and consistency on the server even when client-side validation exists.
- **Operational boundary:** email notifications, file uploads, CRM sync, and analytics are not assumed. Add them only after a real owner workflow and retention/security design are approved.

## Request and error flow

1. The page requests public catalogue data over same-origin `/api/v1/`.
2. The API returns only records marked active/published; empty catalogues have a clear editorial state rather than invented products.
3. The browser sends an enquiry with an explicit intent and optional product selections.
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
