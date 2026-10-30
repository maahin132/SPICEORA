# SPICEORA

SPICEORA is planned as a premium, customer-facing Indian spice-export business website for international B2B buyers, importers, distributors, wholesalers, and related business customers. It is not a SaaS dashboard, ERP, marketplace, or generic landing-page product.

**Working tagline:** “From Indian Origins to Global Markets.”

The current repository contains the Phase 0 technical foundation, Phase 1 planning documents, the Phase 2 responsive homepage, the Phase 3 database-backed product catalogue/read API, the Phase 4 export enquiry workflow, and the Phase 5 Django Admin product content workflow. The local catalogue currently has six category labels and no product records. Enquiries are stored for staff review; no email notification is configured.

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

## Product and design documents

- [Business requirements](./docs/BUSINESS_REQUIREMENTS.md)
- [Information architecture and journeys](./docs/INFORMATION_ARCHITECTURE.md)
- [Application architecture](./docs/ARCHITECTURE.md)
- [Database plan](./docs/DATABASE.md)
- [API plan](./docs/API.md)
- [Visual design brief](./docs/DESIGN_SYSTEM.md)
- [Security plan](./docs/SECURITY.md)
- [Roadmap](./docs/ROADMAP.md)

Decisions required from the owner are labelled **Owner confirmation required**. No company facts, product specifications, certifications, customer evidence, or commercial promises should be published without verification.

## Current homepage

The homepage's product preview is API-driven and keeps the rest of the homepage available when the catalogue API is unavailable. Product detail pages only show admin-published records and link to a product-prefilled enquiry form. Submitted enquiries are available to authorized staff through Django admin. No company contact details are invented, no email provider is configured, and the production privacy/retention and distributed rate-limit controls still require owner review. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for verified scope and checks.
