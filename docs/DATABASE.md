# Database Plan

## Current state

**Implemented:** MySQL 8.0 and Django connection configuration are part of the Phase 0 foundation. Django's built-in auth/admin/session migrations are applied. Phase 3 migration `api.0001_initial` adds `api_productcategory` and `api_product` to `spiceora_db`; it seeds the six owner-provided category labels and creates no product rows. The migration was applied and verified on 2026-10-29. No enquiry tables exist.

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
- `image`: optional Django `ImageField` stored under `MEDIA_ROOT/products/`; admin validation accepts JPG/JPEG/PNG/WebP up to 5 MiB
- `image_alt`: required by model validation when an image is set
- `is_published`: explicit public publication gate; defaults false
- `sort_order`: editorial order
- `created_at`, `updated_at`: timestamps

Only add origin, grade, variety, processing, packaging, certifications, lab results, or other attributes after the owner supplies evidence and confirms they should be public. No products or product claims were seeded.

The Pillow dependency is used by Django's image validation. In development, Django serves uploads at `/media/`; Vite proxies that path to the backend. Production media hosting and delivery are not configured.

### `ExportEnquiry`

**Future proposal only; not implemented.**

- `id`: internal primary key
- `public_reference`: opaque random identifier safe to show to the submitter; never an enumeration of internal records
- `intent`: allow-listed `contact`, `export_enquiry`, or `quotation`
- `contact_name`, `email`: required contact fields (field requirements subject to owner/legal confirmation)
- `company_name`, `country`, `phone`: optional until confirmed as necessary
- `message`: optional, length-limited buyer context
- `privacy_notice_version` and `privacy_notice_acknowledged_at`: record acknowledgement if the final form requires it; not marketing consent
- `status`: staff workflow state such as `new`, `in_progress`, `responded`, `closed`
- `created_at`, `updated_at`

No uploaded documents, identity documents, payment data, or sensitive categories are justified for the initial enquiry workflow. Do not store raw client IPs by default; any abuse signals should be short-lived, access-controlled, and documented.

### `EnquiryItem` — proposed if multi-product enquiries are confirmed

- `id`
- `enquiry_id`: FK to `ExportEnquiry`, cascade on parent deletion only where deletion policy permits
- `product_id`: nullable FK to `Product`, set null if a catalog record is retired/deleted
- `product_name_snapshot`: name as shown when submitted, preserving enquiry meaning
- `quantity_note`: optional bounded free text only if buyers need to describe a requested quantity before units are standardized

Relationship: one enquiry may have zero or more enquiry items; an item can point to a catalog product and stores a display-name snapshot. This supports a buyer requesting a quote for multiple products. Confirm whether multi-product selection is needed at launch; if not, omit `EnquiryItem` and store a single optional product reference on the enquiry.

## Relationships and lifecycle

```text
ProductCategory 1 ─── * Product
ExportEnquiry   1 ─── * EnquiryItem (future proposal only)
Product         1 ─── * EnquiryItem (future proposal only)
```

Retire products by setting `is_published=false` or deactivating their category, not by routine deletion. Public catalogue endpoints exclude unpublished products and products in inactive categories. Django admin is the only catalogue write surface; public write endpoints do not exist.

## Data integrity and operational controls

- The configured MySQL connection uses `utf8mb4`; category and product slugs have unique constraints.
- Apply enquiry plus item inserts in one transaction.
- Store timestamps consistently in UTC.
- Keep database migrations in Django; review and back up before production rollout. Phase 3's additive migration created only the two catalogue tables and inserted the six category labels.
- Grant the runtime account only the permissions required for runtime and planned migrations. Do not run the application as MySQL administrator; consider a separate migration identity in production.
- Do not store secrets in this schema. Keep credentials and Django secrets outside source control.

## Owner confirmation required

- Which of the six requested categories have publishable products at launch?
- Required buyer/contact fields, whether multi-product quotes are required, and supported units/quantity input
- Enquiry retention, deletion/anonymization process, and privacy notice/jurisdiction
- Staff workflow states, access roles, and notification handling
- Product content and any specification fields supported by actual source documentation
