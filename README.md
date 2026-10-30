# SPICEORA

SPICEORA is a premium, customer-facing Indian spice-export business website for international B2B buyers, importers, distributors, wholesalers, and related business customers, with a limited private farm-to-inventory operations foundation. The public website is not a SaaS dashboard, ERP, marketplace, or generic landing-page product.

**Working tagline:** “From Indian Origins to Global Markets.”

The current repository contains the Phase 0 technical foundation, Phase 1 planning documents, the Phase 2 responsive homepage, the Phase 3 database-backed product catalogue/read API, the Phase 4 export enquiry workflow, the Phase 5 Django Admin product content workflow, the Phase 6 owner content-preparation workflow, the Phase 7 internal farm-to-inventory foundation, and the in-progress Phase 8 authentication/operations foundation. No farm, season, harvest, batch, processing, or inventory records are seeded. The product catalogue currently has six category labels and no product records. Customer activation and password recovery use email OTP only; mobile is collected but remains unverified, and SMS is deferred.

## Current stack

- Frontend: React, JavaScript/JSX, Vite, Tailwind CSS, React Router, Lucide React
- Backend: Python, Django, Django REST Framework
- Database: MySQL
- Local secrets: root `.env`, ignored by Git; use `.env.example` as the template

## Local development

See the [Phase 0 setup](./PROJECT_STATUS.md) and [testing guide](./docs/TESTING.md). The frontend and backend currently run as separate development servers. The `/api/health/` route is a liveness check, not a product API or database-readiness endpoint.

The public catalogue is available at `/products/` and `/products/{slug}/`; Django API contracts are documented in [API](./docs/API.md). Set `VITE_API_BASE_URL` only when the frontend needs a different API origin; the default is same-origin `/api/v1` and the Vite development server proxies API and media requests to Django. Do not put credentials in `VITE_*` variables.

After configuring the ignored root `.env`, apply reviewed Django migrations and start the backend from `backend/`:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

In another terminal, start the frontend from `frontend/`:

```powershell
npm run dev
```

The initial catalogue has no product records. Add only owner-approved content and images through the authenticated Django admin before publishing products. Product images are stored locally under `backend/media/products/` during development with randomized filenames and upload validation; production object storage/CDN and media delivery are not configured.

Use the [product content preparation guide](./docs/PRODUCT_CONTENT_PREPARATION.md) and its [owner-editable CSV intake template](./docs/product-content-intake-template.csv) to collect verified details and image assets. The six template rows are blank draft prompts only; they are not products and are never imported automatically.

## Product and design documents

- [Business requirements](./docs/BUSINESS_REQUIREMENTS.md)
- [Information architecture and journeys](./docs/INFORMATION_ARCHITECTURE.md)
- [Application architecture](./docs/ARCHITECTURE.md)
- [Database plan](./docs/DATABASE.md)
- [Product content and image preparation](./docs/PRODUCT_CONTENT_PREPARATION.md)
- [API plan](./docs/API.md)
- [Visual design brief](./docs/DESIGN_SYSTEM.md)
- [Security plan](./docs/SECURITY.md)
- [Roadmap](./docs/ROADMAP.md)

Decisions required from the owner are labelled **Owner confirmation required**. No company facts, product specifications, certifications, customer evidence, or commercial promises should be published without verification.

## Current homepage

The homepage's product preview is API-driven and keeps the rest of the homepage available when the catalogue API is unavailable. Product detail pages only show admin-published records and link to a product-prefilled enquiry form. Submitted enquiries and internal farm/crop/batch/inventory records are available only to authorized staff through Django Admin and protected session-authenticated operations APIs. Staff frontend routes are permission-gated by the backend. The `.env.example` documents personal Gmail SMTP App Password setup for low-volume testing; owner-approved registration and forgot-password OTP delivery was confirmed in a controlled inbox test. Gmail delivery limits and spam controls apply, so it is not represented as production-grade transactional email. SMS is deferred. Production privacy/retention, shared distributed throttling, and deployment controls still require owner review. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for verified scope and checks.
