# Business Requirements

## Status and scope

This document translates the Phase 1 brief into a launch-oriented business requirement set. It is not a claim that the requirements or features have been implemented.

- **Confirmed by owner brief:** SPICEORA is a premium customer-facing Indian spice-export business website serving international B2B buyers, importers, distributors, wholesalers, and related business customers.
- **Confirmed working tagline:** “From Indian Origins to Global Markets.”
- **Confirmed requested category labels:** Cumin, Fennel, Red chilli, Turmeric, Coriander, Dhana-jeera.
- **Confirmed stack:** React/JSX, Vite, Tailwind CSS, React Router, Lucide React; Django REST Framework; MySQL; GitHub.
- **Proposed:** responsive, content-led multi-page company/catalog site with one public enquiry workflow and no buyer dashboard.
- **Owner confirmation required:** every company-specific fact, product detail, export capability, commercial term, privacy policy and operational promise.

## Business goals

1. Help a qualified international buyer understand what product categories SPICEORA can actually supply.
2. Let buyers review approved product information and submit a relevant contact, export or quotation enquiry with minimal friction.
3. Present a credible, polished, consistent brand without unsupported trust claims.
4. Give authorized staff a simple, protected way to maintain approved catalog content and triage enquiries (proposed use of Django admin).

## Non-goals

- SaaS dashboard, ERP, marketplace, public seller portal, buyer account, online checkout or payment collection.
- Pricing engine, instant quotation, inventory/availability promises or automated shipping/customs calculations.
- Product certificates, lab reports, traceability, sourcing/farm claims, export volumes or country lists without verified owner-provided evidence.
- CRM integration, attachments, chat, tracking pixels, elaborate analytics or user-generated reviews in the initial launch.

## Product and content rules

The six category labels in the brief are candidate catalogue groupings, not confirmation of current saleable inventory. Publish a category/product only after the owner confirms availability and provides approved copy and imagery. Do not invent company history, facilities, origin specifics, capacity, markets served, grades, varieties, processing methods, packaging, minimum order quantities, certifications, lab results, testimonials, customer logos, lead times, payment terms, prices or commercial guarantees.

All missing facts must be presented as **Owner confirmation required** in planning, not rendered to public visitors as placeholder claims. Use real approved photography or properly licensed, accurately captioned imagery; never imply that generic stock photography depicts a particular farm, facility, supplier, or product lot.

## Buyer journeys and acceptance outcomes

### 1. Discover products

1. Buyer lands on Home from a search/referral.
2. Sees the business proposition, approved categories and clear route to products.
3. Opens the catalogue and browses/filter categories.
4. Opens an available product detail page.

**Success:** the buyer can reach a published product in a few clear actions on mobile or desktop. If no approved items exist, show a truthful contact invitation rather than fabricated stock.

### 2. Explore an individual product

1. Buyer opens a product from the catalogue or a shared URL.
2. Reviews approved description, category, real imagery and only verified supply/specification details.
3. Uses a contextual “Enquire about this product” or “Request a quotation” action.

**Success:** the selected product is carried into the enquiry form and clearly shown before submission. Unknown data is omitted, not filled with assumptions.

### 3. Submit an export enquiry

1. Buyer opens Contact & export enquiry.
2. Chooses/indicates export enquiry intent; enters only necessary contact and request details.
3. Reviews the privacy notice and submits.
4. Sees an honest receipt confirmation and opaque reference, without guaranteed response timing.

**Success:** valid submissions are stored, abuse controls are applied, and only authorized staff can access the record. Exact follow-up process and acknowledgement copy require owner approval.

### 4. Request a quotation

1. Buyer chooses “Request a quotation” from a product detail page or contact page.
2. Selected product(s) are prefilled; buyer can add a bounded optional quantity note if approved.
3. Buyer submits the enquiry and receives a confirmation.

**Success:** the system routes a quotation request to staff as an enquiry, not an instant price. Do not imply availability, quote currency, MOQ, freight, lead time or price validity before the business supplies those policies.

### 5. Contact the company

1. Buyer opens Contact & export enquiry.
2. Finds owner-confirmed business email/phone/address only if approved for public display, or uses the enquiry form.
3. Sends a general contact message.

**Success:** contact channels are accurate and monitored. **Owner confirmation required:** public contact details, recipient inbox, operating hours and response expectations.

### 6. Understand the export and enquiry process

1. Buyer opens an Export process page/section.
2. Reviews only verified steps, required documents, responsibility boundaries and what happens after an enquiry.
3. Continues to the enquiry form.

**Success:** explain only the business’s actual process. Do not imply SPICEORA handles all shipping, customs, certificates, inspection or payment steps unless confirmed.

## Owner confirmation register

Resolve before relevant content or data collection is launched:

1. Legal/display company name, ownership/registration facts, approved address, phone, email and support owner.
2. Which categories and specific products are genuinely available; approved names, descriptions, images, origin statements and product specifications.
3. Verified certifications, lab/testing claims, quality procedures, export countries, volumes, capacity, customer references and logo/image rights, if any.
4. Export process, supported markets, documentation, incoterms, shipping, packaging, order quantities, payment terms, quoting currency, lead times and response expectations.
5. Required form fields, quotation item/quantity behavior, routing mailbox, staff workflow, response ownership and retention/deletion schedule.
6. Applicable privacy jurisdiction, controller/contact details, lawful basis, notice text, retention, data location, international transfers and request handling.
7. Approved brand assets, photography rights, typography/font licenses, language/currency requirements, domain, hosting/data region and deployment owner.

Until confirmed, treat these as unanswered—not as facts that can be filled from industry convention.
