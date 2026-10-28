# Database Plan

## Current state

**Existing:** MySQL 8.0 and Django connection configuration are part of the Phase 0 foundation. Django's built-in auth/admin/session migrations are applied. No SPICEORA product or enquiry tables exist in this phase.

**Phase 1:** This is a proposed logical model only. Do not create tables or migrations until Phase 2 is explicitly approved and the owner confirms the required business fields.

## Proposed entities

### `ProductCategory`

- `id`: internal primary key
- `slug`: unique stable URL identifier
- `name`: approved display name
- `sort_order`: editorial ordering
- `is_active`: whether the category is published

Initial category labels provided by the owner: Cumin, Fennel, Red chilli, Turmeric, Coriander, Dhana-jeera. Their inventory availability and final editorial naming still require owner confirmation. A category record does not imply that products are currently available.

### `Product`

- `id`
- `category_id`: required FK to `ProductCategory` (protect referenced categories)
- `slug`: unique stable URL identifier
- `name`, `summary`, `description`: owner-approved editorial content
- `is_active`: publication state
- `sort_order`
- `created_at`, `updated_at`

Only add origin, grade, variety, processing, packaging, certifications, lab results, images, or other attributes when the owner supplies verified values and confirms that they should be public. Avoid an unvalidated JSON “specifications” bucket or price/MOQ promises.

### `ExportEnquiry`

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
ExportEnquiry   1 ─── * EnquiryItem (optional launch scope)
Product         1 ─── * EnquiryItem (optional, nullable historical reference)
```

Retire public products with `is_active=false`, not routine hard deletion. Public list/detail APIs must exclude inactive records; preserve historical enquiry snapshots. Restrict staff changes through Django admin permissions. Define any purge/anonymization workflow only after the retention policy and legal obligations are confirmed.

## Data integrity and operational controls

- Use `utf8mb4`; use database constraints for unique slugs, valid intent/status values, and required fields.
- Apply enquiry plus item inserts in one transaction.
- Store timestamps consistently in UTC.
- Keep database migrations in Django; review and back up before production rollout.
- Grant the runtime account only the permissions required for runtime and planned migrations. Do not run the application as MySQL administrator; consider a separate migration identity in production.
- Do not store secrets in this schema. Keep credentials and Django secrets outside source control.

## Owner confirmation required

- Which of the six requested categories have publishable products at launch?
- Required buyer/contact fields, whether multi-product quotes are required, and supported units/quantity input
- Enquiry retention, deletion/anonymization process, and privacy notice/jurisdiction
- Staff workflow states, access roles, and notification handling
- Product content and any specification fields supported by actual source documentation
