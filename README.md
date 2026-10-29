# SPICEORA

SPICEORA is planned as a premium, customer-facing Indian spice-export business website for international B2B buyers, importers, distributors, wholesalers, and related business customers. It is not a SaaS dashboard, ERP, marketplace, or generic landing-page product.

**Working tagline:** “From Indian Origins to Global Markets.”

The current repository contains the Phase 0 technical foundation, Phase 1 planning documents, and the Phase 2 responsive homepage/shared visual foundation. The backend currently exposes only its health endpoint and Django admin. The homepage catalogue is an illustrative category preview, not a live catalog; its enquiry area is a clearly marked placeholder and does not accept or send enquiries. Product APIs, enquiry handling, and business database entities are not implemented.

## Current stack

- Frontend: React, JavaScript/JSX, Vite, Tailwind CSS, React Router, Lucide React
- Backend: Python, Django, Django REST Framework
- Database: MySQL
- Local secrets: root `.env`, ignored by Git; use `.env.example` as the template

## Local development

See the [Phase 0 setup](./PROJECT_STATUS.md) and [testing guide](./docs/TESTING.md). The frontend and backend currently run as separate development servers. The `/api/health/` route is a liveness check, not a product API or database-readiness endpoint.

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

The homepage is a visual foundation only. The category tiles lead to an enquiry placeholder; there is no product catalogue, contact channel, enquiry form, or backend submission endpoint yet. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for verified scope and checks.
