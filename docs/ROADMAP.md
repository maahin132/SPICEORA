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

## Phase 5 — admin product management and content workflow

**Complete:** Django Admin supports product/category content management, publishing, ordering, search/filter, image previews, validated randomized image uploads, and relationship-protected deletion. Existing public catalogue routes and layouts consume the same API fields; no product records or invented product claims were added.

Before production, configure and verify media storage/delivery, backup and retention, CDN/security headers, and any desired image malware/content scanning. Populate the catalogue only with owner-approved product content.

## Phase 6 — real product catalogue and content preparation

**Content preparation complete; catalogue remains intentionally empty.** Added a blank CSV intake template for the six existing categories, image/content verification guidance, route-specific page titles/descriptions, and a clearer empty catalogue enquiry action. No products or schema changes were added.

The owner must provide and approve each actual product name, category, short summary, full description, publication order, authentic image and rights, and descriptive alt text. Variant, grade, origin, processing, packaging, minimum order quantity, export documentation, and certifications require owner evidence and review before any public use. They are intake-only fields and not part of the current product model/API.

Route-specific title and description metadata is client-side only. Review server-rendered/prerendered SEO and canonical URLs after the public domain and hosting architecture are approved.

## Phase 7 — own farm and crop traceability foundation

**Operational foundation implemented.** The additive schema records staff-entered farms, crop seasons, harvests, production batches, actual processing events, and append-only inventory movements. Batch creation records the initial production receipt; balances are calculated from the movement ledger. No operational records are seeded, and no farm or processing capability is presumed.

The Django Admin and protected session-authenticated, per-model-permission API are the current staff surfaces. The public React app does not have secure staff authentication or CSRF handling, so there is no operations frontend. Before production use, define operational reference conventions, staff access assignments, reservation/order linkage, stock correction approval ownership, backup/audit controls, and a secure staff frontend only if needed. Exercise MySQL row-lock behavior under concurrency in a representative deployment; the isolated SQLite suite does not prove that behavior.

Phase 7 stopped at the internal traceability foundation and was approved as the baseline for Phase 8.

## Phase 8 — authentication, OTP verification and operations dashboard

**Implementation in progress.** Customer/staff session authentication, email-only OTP activation and recovery, Gmail SMTP integration using a Google App Password, and a permission-aware React operations console have been added. Mobile verification and SMS recovery are deferred; the existing Django user model is preserved and the account migration is additive.

Do not treat registration or recovery delivery as production-ready until Gmail SMTP settings and an App Password are configured and a test OTP is received in an owner-approved inbox. Gmail SMTP is a low-volume, best-effort option, not a transactional email guarantee. No SMS provider or paid plan may be enabled. Finish backend and browser/responsive QA, inspect secret/diff state, and re-verify permission and CSRF behavior before any Phase 8 completion claim. Do not start Phase 9 without explicit owner approval.

## Deferred / only if justified

Localization, search, multiple currencies, CRM integration, enquiry attachments, buyer accounts, analytics, custom admin dashboards, and advanced catalogue filtering require an evidenced business need and owner approval. Do not build a SaaS/ERP/marketplace surface.
