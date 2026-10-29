# Information Architecture and User Journeys

## Phase 2 implementation status

The current homepage realizes the Home page direction and shared header/footer. The six category cards are illustrative links to an enquiry placeholder, not a live catalogue or proof of availability. The enquiry section does not accept submissions. Other proposed routes remain unimplemented.

## Sitemap recommendation

```text
/
├── /products/
│   └── /products/{product-slug}/
├── /contact/                 (contact + export enquiry + quotation form)
├── /privacy/
├── /about/                   (defer as a separate page until verified content exists)
└── /export-process/          (defer as a separate page; initially a concise verified section)
```

The main navigation should stay customer-oriented: **Products**, **About** (only when supported), **Export process** (only when useful/verified), and **Contact**. Use one prominent **Request a quotation** CTA. Do not create dashboard-style navigation, accounts, seller portals or unrelated category pages.

## Page plan

| Page | Launch recommendation and purpose | Key sections | Primary CTA | Required data | Mobile behavior |
|---|---|---|---|---|---|
| Home `/` | Essential. Establish the brand and direct B2B buyers to actual products or an enquiry. | Editorial hero/tagline; available categories; concise value proposition using only verified facts; product feature; verified process/quality information when available; enquiry close. | Explore products; secondary Request a quotation | Approved brand copy, published categories/products, rights-cleared authentic imagery, confirmed proof points (optional). | Single-column narrative; concise hero; horizontal category overflow only if accessible; stacked CTAs; no autoplay hero. |
| Products `/products/` | Essential. Browse currently published catalogue. | Intro; category navigation/filter; product list with clear names and concise approved summaries; honest empty state. | Open product; Request a quotation | Active products/categories, slugs, summaries, images/alt text if provided. | One-column list or modest two-column grid when legible; filter becomes keyboard-accessible select/disclosure; no oversized filters sidebar. |
| Product detail `/products/{slug}/` | Essential template for each approved item. | Breadcrumb; product name/category; authentic image and caption; approved description; verified attributes only; availability/contact caveat if needed; enquiry CTA. | Enquire about this product / Request a quotation | Published product record and approved content; item prefill identifier. | Image and content stack; CTA easy to reach without covering content; all specs readable without horizontal scroll. |
| Contact & export enquiry `/contact/` | Essential. One path for general contact, export enquiries and quotation requests. | Confirmed contact channels; short form with intent; product selection/context; privacy notice link; acknowledgement/error states. | Submit enquiry / Request a quotation | Recipient/workflow, approved form fields, active product list, privacy notice, abuse handling. | Single-column labeled fields; suitable email keyboard; visible errors and focus; submit state accessible; no intrusive modal. |
| Privacy `/privacy/` | Essential if personal information is collected; publish reviewed notice before form is enabled. | Controller/contact; data collected; purpose/legal basis; sharing/transfers; retention; rights/request channel; cookies/analytics if used. | Contact privacy owner | Jurisdiction and legal owner review, actual processing/hosting/retention. | Readable narrow text measure, descriptive headings, in-page navigation only if long. |
| About `/about/` | Useful but can wait as a standalone page. Initially a small verified company introduction on Home. | Company identity, real sourcing/operations, team/facility only if owner confirms and supplies evidence. | Contact the company | Legal/display identity and verified narrative/assets. | Short paragraphs, no unverified timeline or decorative statistic blocks. |
| Export process `/export-process/` | Useful but can wait as a standalone page. Initially a concise verified explainer on Home or Contact. | Actual enquiry-to-fulfillment steps, roles, documents and boundaries. | Start an export enquiry | Owner-confirmed operating process and market-specific caveats. | Ordered, short steps; avoid dense process diagrams on small screens. |

### Launch scope

**Essential:** Home, Products, Product detail template, Contact & export enquiry, Privacy. About and Export process can begin as verified sections on Home/Contact and become pages only when there is enough accurate content. The contact/enquiry page can offer both direct contact information and the form after the owner confirms those channels.

**Do not publish empty/invented content to fill a page.** If the owner has not supplied catalog content, launch should be gated or present a truthful “contact us for current product availability” message.

## Journeys

See [business requirements](./BUSINESS_REQUIREMENTS.md) for detailed journey steps and outcomes. Route map:

- Discover: Home → Products → Product detail.
- Product question: Product detail → Contact form with product context → confirmation.
- Quote: product or catalogue → Contact form with quote intent and optional multiple products → confirmation.
- General contact: Contact → confirmed channels or general enquiry → confirmation.
- Process research: Home/Export process → Contact enquiry.
- Privacy: form → Privacy notice before submission; privacy page remains reachable from footer.

Every route should support direct linking, browser back/forward, keyboard navigation and a useful not-found state. Do not require an account to browse or submit an enquiry.

## Shared design and interaction rules

- Persistent but restrained brand header; mobile navigation exposes the same destinations and closes after selection.
- Every page has a clear next action, readable hierarchy, accessible focus and footer links to Contact and Privacy.
- Product-to-enquiry context is explicit and can be removed/changed by the buyer.
- Form submission has loading, field error, success and retryable server-failure states. Success copy does not invent an SLA.
- On small viewports, prevent horizontal scrolling, keep touch targets comfortable, and avoid sticky controls obscuring content.

## Content dependencies

The owner must confirm business identity/contact details, publishable products and assets, export workflow, privacy policy and enquiry handling before launch. See [business confirmation register](./BUSINESS_REQUIREMENTS.md#owner-confirmation-register).
