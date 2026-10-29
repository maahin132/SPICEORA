# Roadmap

## Phase 0 — foundation

**Complete:** React/Vite and Django/DRF foundation, local MySQL setup, health endpoint, environment-based configuration, documentation skeleton, and GitHub workflow templates.

## Phase 1 — requirements and architecture

**Documentation complete; owner decisions remain open.** Business requirements, buyer journeys, sitemap, proposed application/database/API architecture, security and testing plan, and original visual design brief are documented. No business pages, product APIs, schema, dependencies, or application code were added.

Before implementation approval, resolve the owner confirmations in [business requirements](./BUSINESS_REQUIREMENTS.md), [information architecture](./INFORMATION_ARCHITECTURE.md), and [database plan](./DATABASE.md). Especially confirm legal/company contact details, real product availability/content, export process/claims, privacy obligations and enquiry operations.

## Phase 2 — homepage and visual foundation

**Complete:** responsive homepage, shared accessible header/navigation/footer, visual tokens, local illustrative photography, image fallback and phase-appropriate documentation/browser checks.

The category cards are illustrative, and the enquiry section is a non-submitting placeholder. Catalogue/detail pages, enquiry submission, business APIs and schema changes remain out of scope.

## Phase 3 — product catalogue and read API

**Implemented:** separate product category/product models; six category labels without product records; staff catalogue management in Django admin; active-only category and published product read APIs; pagination and category filtering; responsive React catalogue and product detail routes; API loading, empty, error, and not-found states.

No product/demo records, product availability claims, or unverified product facts were added. Enquiry, quotation, contact submission, and payments are not part of this phase.

## Phase 4 — enquiry planning and implementation (not started)

Proceed only after owner/legal confirmation of contact fields, recipient workflow, privacy notice/jurisdiction, retention, multi-product behavior, and abuse-response operations. Then implement the approved data model, protected staff workflow, validated/rate-limited public submission endpoint, and accessible frontend submission states.

## Deferred / only if justified

Localization, search, multiple currencies, CRM integration, enquiry attachments, buyer accounts, analytics, custom admin dashboards, and advanced catalogue filtering require an evidenced business need and owner approval. Do not build a SaaS/ERP/marketplace surface.
