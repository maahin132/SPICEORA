# Database Plan

## Current state

**Implemented:** MySQL 8.0 and Django connection configuration are part of the Phase 0 foundation. Django's built-in auth/admin/session migrations are applied. Phase 3 migration `api.0001_initial` adds `api_productcategory` and `api_product` to `spiceora_db`; it seeds the six owner-provided category labels and creates no product rows. Phase 4 migration `api.0002_exportenquiry` was applied on 2026-10-30 and adds the single `api_exportenquiry` table. Phase 5 migration `api.0003_phase5_product_admin_safety` changes ORM deletion behavior and upload-field state only; reviewed generated SQL contained no database operations. Current verified counts are six categories, zero products, and one enquiry. The enquiry was preserved without reading or editing its content. No unrelated databases were accessed or changed.

The configured development connection was verified as `spiceora_db` at `localhost`. The two catalogue tables use MySQL collation `utf8mb4_0900_ai_ci`. No WoodHub or unrelated database was accessed or changed.

## Implemented catalogue entities

### `ProductCategory`

- `id`: internal primary key
- `slug`: unique stable identifier
- `name`: unique category label
- `sort_order`: editorial ordering
- `is_active`: staff-controlled category visibility

Initial migration labels: Cumin, Fennel, Red chilli, Turmeric, Coriander, Dhana-jeera. These are category labels only and do not imply saleable product availability.

### `Product`

- `id`: internal primary key
- `category_id`: required FK to `ProductCategory`, protected from deletion while referenced
- `slug`: unique stable URL identifier
- `name`, `summary`, `description`: staff-entered, owner-approved public content
- `image`: optional Django `ImageField` stored under `MEDIA_ROOT/products/`; admin validation accepts matching JPG/JPEG/PNG/WebP content and extensions up to 5 MiB, 8,000 px per side, and 40 megapixels; new uploads use random UUID filenames
- `image_alt`: required by model validation when an image is set
- `is_published`: explicit public publication gate; defaults false
- `sort_order`: editorial order
- `created_at`, `updated_at`: timestamps

Only add origin, grade, variety, processing, packaging, certifications, lab results, or other attributes after the owner supplies evidence and confirms they should be public. No products or product claims were seeded.

The Pillow dependency is used by Django's image validation. Existing image paths are not rewritten by the Phase 5 migration, and old image files are not automatically deleted when a product image is replaced or cleared. In development, Django serves uploads at `/media/`; Vite proxies that path to the backend. Production media hosting, CDN, scanning and delivery are not configured.

### `ExportEnquiry`

**Implemented:** a single incoming buyer request; no multi-item quotation workflow.

- `id`: internal primary key
- `public_reference`: unique opaque UUID receipt reference; no public lookup endpoint
- `full_name`, `email`, `country`: required contact fields
- `company_name`, `phone`, `message`: optional bounded input
- `category_id`: required protected FK to the selected active category
- `product_id`: optional FK to a published product; product deletion is protected while an enquiry references it so the relationship is preserved
- `product_name_snapshot`: product display name at submission, for historical context
- `quantity`, `quantity_unit`: required by the public API; positive decimal estimate and one of `kg` or `metric_tonne`
- `status`: `new`, `in_progress`, `responded`, or `closed`
- `internal_notes`: staff-only notes, never exposed by the public API
- `created_at`, `updated_at`

A database check constraint requires quantity to be null with a blank unit, or positive with an allowed unit. The public API requires quantity and unit, exactly one category or product selector, and derives product category on the server. Null quantities remain representable for staff-created historical/imported records.

No uploaded documents, identity documents, payment data, or sensitive categories are justified for the initial enquiry workflow. Do not store raw client IPs by default; any abuse signals should be short-lived, access-controlled, and documented.

There is no `EnquiryItem` table. Multiple product line items and a quotation workflow are deferred until confirmed as necessary.

## Relationships and lifecycle

```text
ProductCategory 1 ─── * Product
ProductCategory 1 ─── * ExportEnquiry
Product         0..1 ─── * ExportEnquiry
```

Retire products by setting `is_published=false` or deactivating their category, not by routine deletion. Product deletion is protected while enquiry records reference it; category deletion is protected while products or enquiries reference it. Public catalogue endpoints exclude unpublished products and products in inactive categories. Django admin is the catalogue write surface; the only public write endpoint creates enquiries, with no public read or update operation.

## Data integrity and operational controls

- The configured MySQL connection uses `utf8mb4`; category and product slugs have unique constraints.
- Enquiry creation is one atomic database insert; there are no separate item rows.
- Store timestamps consistently in UTC.
- Keep database migrations in Django; review and back up before production rollout. Phase 3's additive migration created only the two catalogue tables and inserted the six category labels.
- Grant the runtime account only the permissions required for runtime and planned migrations. Do not run the application as MySQL administrator; consider a separate migration identity in production.
- Do not store secrets in this schema. Keep credentials and Django secrets outside source control.

## Owner confirmation required

- Which of the six requested categories have publishable products at launch?
- Whether multi-product quotes or additional quantity units are needed
- Enquiry retention, deletion/anonymization process, and privacy notice/jurisdiction
- Staff workflow states, access roles, and notification handling
- Product content and any specification fields supported by actual source documentation
