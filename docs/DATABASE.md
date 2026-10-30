# Database Plan

## Current state

**Implemented:** MySQL 8.0 and Django connection configuration are part of the Phase 0 foundation. Django's built-in auth/admin/session migrations are applied. Phase 3 migration `api.0001_initial` adds `api_productcategory` and `api_product` to `spiceora_db`; it seeds the six owner-provided category labels and creates no product rows. Phase 4 migration `api.0002_exportenquiry` was applied on 2026-10-30 and adds the single `api_exportenquiry` table. Phase 5 migration `api.0003_phase5_product_admin_safety` changes ORM deletion behavior and upload-field state only; reviewed generated SQL contained no database operations. Current verified counts are six categories, zero products, and one enquiry. The enquiry was preserved without reading or editing its content. No unrelated databases were accessed or changed.

Phase 6 adds an owner-editable CSV intake template under `docs/`, not database records or schema. No Django model or API migration is required. Intake rows remain draft and unverified until the owner supplies evidence and approves publication through Django Admin.

Phase 7 migration `api.0004_farm_cropseason_harvest_productionbatch_and_more` creates six new operational tables and their check/foreign-key constraints in `spiceora_db`. Generated SQL was reviewed before application: only new tables, constraints and protected foreign keys are created; no existing table is altered or dropped and no existing rows are updated or deleted. The migration contains no data seeding. Post-migration verification confirmed all existing category/product/enquiry counts unchanged and all six new operational tables empty.

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

## Phase 7 farm-to-inventory entities

### `Farm`

Unique staff-entered reference and name, location/address, optional paired area/unit, description, private internal notes, active state, and timestamps. No farm names, locations, areas, or records are seeded. Farm identity/location/area are protected from edits after seasons are recorded; a farm with seasons cannot be deleted.

### `CropSeason`

Unique reference, protected farm FK, staff-entered crop name, optional planting and expected harvest dates, status (`planned`, `growing`, `harvested`, `closed`, `cancelled`), private notes, and timestamps. Multiple seasons may belong to one farm. Expected harvest cannot precede planting. A season with harvests cannot have its farm, crop identity, or planting date rewritten.

### `Harvest`

Unique reference, protected crop-season FK, actual harvest date, positive decimal quantity and mass unit (`kg` or `metric_tonne`), notes, and timestamps. Harvest date cannot precede planting or be in the future. Production batches can split a harvest but their combined initial quantities cannot exceed the recorded harvest amount after unit conversion. Once a batch references a harvest, its origin/date/quantity are immutable.

### `ProductionBatch`

Unique reference, protected harvest FK, staff-entered product/spice identification (not an FK to the public product catalogue), batch date, positive initial quantity/unit, current handling status, internal notes, and timestamps. The batch date cannot precede harvest or be in the future. Batch reference, origin, product identity, date, and initial quantity are immutable. Creating a batch in Django Admin or through the protected API atomically creates one production-receipt movement for its initial quantity; no batch rows are seeded.

### `ProcessingRecord`

Protected batch FK, free-text activity, actual activity date, optional paired input/output quantities and units, description, supporting document references, private notes, and timestamps. Actual activity dates cannot precede batch creation or be future dates. Records are append-only. A processing record does not itself change inventory; record real stock adjustments separately. Supporting document references are text only—there is no upload or document-serving endpoint.

### `InventoryMovement`

Unique reference, protected batch FK, explicit movement type, positive quantity and unit, movement date, required reason/reference, private notes, and creation timestamp. Records are append-only and cannot be deleted through model/admin/API operations. Movement dates cannot predate the batch, be in the future, or be earlier than the latest movement for that batch. Corrections are new, permission-gated movements; do not edit or overwrite the ledger.

## Inventory ledger and calculation

All movement quantities are normalized to kilograms (`1 metric_tonne = 1000 kg`) for calculations. Each batch begins with one automatically generated production receipt equal to its initial quantity.

- **On-hand kg:** production receipts + processing increases + approved correction increases − processing decreases − dispatches − approved correction decreases.
- **Reserved kg:** reservations − reservation releases − dispatched quantity allocated first against the pooled reserved amount (never below zero).
- **Available kg:** on-hand kg − reserved kg.

Reservations and outflows are checked inside a transaction while locking the batch row. A reservation or non-dispatch decrease cannot make available stock negative; a dispatch cannot exceed physical on-hand stock and consumes the pooled reserved balance first. Releases cannot exceed outstanding reservations. This system does not associate reservations with individual buyers/orders; dispatch uses pooled reservations. Staff must record actual processing inventory effects separately from processing narrative events. No mutable stock balance column is stored, and no movement is silently overwritten. Concurrency guarantees depend on the configured MySQL row lock; SQLite tests do not establish MySQL concurrency behavior.

### Traceability relationships

```text
Farm 1 ─── * CropSeason 1 ─── * Harvest 1 ─── * ProductionBatch
ProductionBatch 1 ─── * ProcessingRecord
ProductionBatch 1 ─── * InventoryMovement
```

The public Product/ExportEnquiry models and relationships are unchanged. Farm and operational data are not exposed by anonymous endpoints.

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
