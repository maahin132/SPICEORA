# Product Content Preparation

## Owner-editable intake template

Use [`product-content-intake-template.csv`](./product-content-intake-template.csv) to collect candidate content for the six existing catalogue categories. The rows are blank intake prompts, **not product records**, evidence of stock, or authorization to publish. Do not import this file into production.

For each real product the owner wants considered, create a separate row and provide:

- **Core catalogue content:** owner-approved product name, one existing category, concise summary, full description, publication status (`draft` until approval), and display order.
- **Image content:** supplied image filename and descriptive alt text. Omit the image until an authentic, rights-cleared product photograph is provided.
- **Verification:** set `content_verification_status` to `verified` only after review; identify the source/document and approval date. Otherwise leave it `unverified`.
- **Optional business details:** product variant, available grade, origin, processing, packaging, minimum order quantity, export documentation, certifications, and additional buyer notes. Treat every one of these as **unverified until the owner supplies supporting evidence and approves public use**. They are intake-only columns and are not currently stored or exposed by the product model or API.

Leave unsupported values blank. In particular, do not infer product identity, grade, origin, processing, packaging, quantities, export capability, documentation, or certification from industry norms or category names. Do not invent testimonials, supplier claims, prices, stock, or export promises.

The public model currently supports name, slug, category, short summary, full description, one optional main image, image alt text, draft/published state, display order, and timestamps. Do not mark an item published until its core fields and image rights (if applicable) have been reviewed by the owner and the owner explicitly approves publication in Django Admin.

## Product image requirements

- **Source:** genuine product photography supplied or explicitly approved by the owner, representing the actual item being described. No random stock image should be presented as a SPICEORA product.
- **Preferred crop:** square (1:1), with the product centered and breathing room around it. The site uses near-square detail imagery and a slightly landscape product-card crop, so keep important content away from the edges.
- **Preferred resolution:** 1600 × 1600 pixels or higher. Provide a sharp original; the upload limit is 8000 pixels on either side and 40 megapixels total.
- **Accepted formats:** JPG/JPEG, PNG, or WebP. The image content must match the extension.
- **Maximum upload size:** 5 MiB. The authenticated Django Admin validates image content, format, dimensions, and size.
- **Composition:** natural, even light; accurate color; clean, quiet background; one clear subject; no text overlays, logos, packaging labels, or props that imply unverified claims. Avoid heavy saturation and excessive processing.
- **Suggested source filename before upload:** `category-product-view-YYYYMM-v01.jpg`, lowercase ASCII with hyphens. The application stores each new upload with a random UUID filename under `MEDIA_ROOT/products/`; do not rely on the submitted filename becoming the public URL.
- **Alt text:** concise description of what is visibly present, such as “Whole cumin seeds in a shallow ceramic dish.” Do not add origin, grade, quality, availability, certification, or other information that cannot be confirmed from the image and approved product record. Do not begin with “image of”.
- **Rights:** record the owner/source and usage permission alongside the source document before publication. No image licensing or product photography is inferred by this template.

Local development serves media through Django in debug mode and the Vite `/media` proxy. Production media hosting, CDN, backup/retention, scanning, and delivery headers are not configured.

## Buyer-facing content and search presentation

- Keep the product title identical to the owner-approved product name and keep the slug stable after publication.
- Write the summary as a short, factual description of the supplied item. Use the full description for additional owner-verified context.
- Current product pages use the product name for the browser title and the approved short summary (truncated to a safe metadata length) for the meta description. No structured data for unknown product specifications is generated. A production canonical URL is not set until the approved public domain is known.
- The site is a client-rendered React application; route metadata changes in the browser after the app loads. The initial HTML still contains generic SPICEORA metadata, and server-side rendering/prerendering is not configured. Reassess rendered SEO after the production domain and deployment architecture are approved.
- Keep category, product name, summary, alt text, and enquiry selection consistent. Product-detail enquiry links carry the published product slug and its current category slug.
- If a product is renamed after publication, check any shared links and coordinate an approved redirect before changing its slug. Redirect management is not currently implemented.
