# Roadmap

## Phase 0 — foundation

**Complete:** React/Vite and Django/DRF foundation, local MySQL setup, health endpoint, environment-based configuration, documentation skeleton, and GitHub workflow templates.

## Phase 1 — requirements and architecture

**Documentation complete; owner decisions remain open.** Business requirements, buyer journeys, sitemap, proposed application/database/API architecture, security and testing plan, and original visual design brief are documented. No business pages, product APIs, schema, dependencies, or application code were added.

Before implementation approval, resolve the owner confirmations in [business requirements](./BUSINESS_REQUIREMENTS.md), [information architecture](./INFORMATION_ARCHITECTURE.md), and [database plan](./DATABASE.md). Especially confirm legal/company contact details, real product availability/content, export process/claims, privacy obligations and enquiry operations.

## Phase 2 — homepage and visual foundation

**Complete:** responsive homepage, shared accessible header/navigation/footer, visual tokens, local illustrative photography, image fallback and phase-appropriate documentation/browser checks.

The homepage foundation is complete. Its enquiry call to action now links to the Phase 4 working enquiry form.

## Phase 3 — product catalogue and read API

**Implemented:** separate product category/product models; six category labels without product records; staff catalogue management in Django admin; active-only category and published product read APIs; pagination and category filtering; responsive React catalogue and product detail routes; API loading, empty, error, and not-found states.

No product/demo records, product availability claims, or unverified product facts were added. Enquiry, quotation, contact submission, and payments are not part of this phase.

## Phase 4 — export enquiry system

**Implemented:** validated category/product enquiry submission; responsive form with product-specific preselection; receipt reference; server-side validation; IP rate limit; and Django admin status/notes workflow. No email provider, multi-product quotation flow, or public enquiry lookup exists.

Before public production launch, obtain owner/legal approval for the privacy notice and retention/deletion policy; configure a shared production throttle cache and edge abuse controls; confirm staff who will handle submissions; and configure/test a notification provider only if the owner approves that workflow.

## Deferred / only if justified

Localization, search, multiple currencies, CRM integration, enquiry attachments, buyer accounts, analytics, custom admin dashboards, and advanced catalogue filtering require an evidenced business need and owner approval. Do not build a SaaS/ERP/marketplace surface.
