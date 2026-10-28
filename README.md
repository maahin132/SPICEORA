# SPICEORA

SPICEORA is planned as a premium, customer-facing Indian spice-export business website for international B2B buyers, importers, distributors, wholesalers, and related business customers. It is not a SaaS dashboard, ERP, marketplace, or generic landing-page product.

**Working tagline:** “From Indian Origins to Global Markets.”

The current repository is the Phase 0 technical foundation. The frontend is still a placeholder, and the backend currently exposes only its health endpoint and Django admin. Phase 1 records approved direction and proposals; it does not implement business pages, product APIs, enquiry handling, or a business data model.

## Current stack

- Frontend: React, JavaScript/JSX, Vite, Tailwind CSS, React Router, Lucide React
- Backend: Python, Django, Django REST Framework
- Database: MySQL
- Local secrets: root `.env`, ignored by Git; use `.env.example` as the template

## Local development

See the [Phase 0 setup](./PROJECT_STATUS.md) and [testing guide](./docs/TESTING.md). The frontend and backend currently run as separate development servers. The `/api/health/` route is a liveness check, not a product API or database-readiness endpoint.

## Phase 1 planning documents

- [Business requirements](./docs/BUSINESS_REQUIREMENTS.md)
- [Information architecture and journeys](./docs/INFORMATION_ARCHITECTURE.md)
- [Application architecture](./docs/ARCHITECTURE.md)
- [Database plan](./docs/DATABASE.md)
- [API plan](./docs/API.md)
- [Visual design brief](./docs/DESIGN_SYSTEM.md)
- [Security plan](./docs/SECURITY.md)
- [Roadmap](./docs/ROADMAP.md)

Decisions required from the owner are labelled **Owner confirmation required**. No company facts, product specifications, certifications, customer evidence, or commercial promises should be published without verification.
