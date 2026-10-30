# Security Plan

## Scope and implementation status

This document defines current controls and remaining launch requirements. It is not a security certification. The current code has environment-based Django settings, explicit development CORS configuration, Django's standard middleware, a public health endpoint, read-only catalogue endpoints, and a public enquiry-create endpoint. Production deployment controls and a verified security review are not implemented.

The anonymous catalogue API returns only products marked published and belonging to active categories. The category list exposes active owner-provided labels for selection, without asserting availability. Product detail returns 404 for missing, unpublished, or inactive-category products. Admin is the only catalogue write surface and uses Django's authenticated, CSRF-protected session admin.

Product image uploads are available only through authenticated Django Admin. Server-side validation accepts matching JPG/JPEG, PNG, or WebP content and extensions; limits files to 5 MiB, 8,000 px per side, and 40 megapixels; and gives new uploads random UUID filenames under `products/`. Alternative text is required when an image is supplied. Old files are not automatically removed on image replacement/removal. Development uploads are served by Django only in DEBUG mode. Production media hosting, malware/content scanning, and CDN policy are not implemented and must be designed before production uploads are enabled. These checks do not replace production storage isolation, content scanning, or safe response headers.

The Phase 6 intake CSV is documentation, not application input: it is not automatically imported, does not create products, and optional unverified claims must not be copied into public records without evidence and owner approval. Do not put credentials or buyer personal information in the intake file.

The public enquiry endpoint stores submitted contact/business data and returns a generic receipt reference. Server-side validation enforces required fields, bounds, category/product visibility, and quantity-unit pairing. The public response does not return enquiry details, status, or internal notes. No email or other notification provider is configured.

Phase 7 farm, crop season, harvest, batch, processing and inventory data are private operational records. They are available through authenticated Django Admin and `/api/v1/operations/` staff collections only. API access requires a staff user plus per-model view/add permissions; unsafe session-authenticated requests retain CSRF protection. Correction movements require the additional `approve_inventory_correction` model permission. There are no anonymous operations reads, public write endpoints, or operations routes in the React site. Internal notes and document references are not serialized by public catalogue/enquiry endpoints.

Processing records and inventory movements are append-only in model/admin/API paths. Batch origin/identity/initial quantity are immutable, and farm/season/harvest relationships use protected foreign keys and admin deletion restrictions. Inventory writes lock the batch row and reject reservations/outflows that would make available stock negative; production batch creation and its initial receipt are transactional. This is application-level workflow protection, not tamper-proof ledger storage: database administrators can still alter rows, and database auditing/backup/restore controls remain deployment responsibilities.

## Secrets and configuration

- Keep `DJANGO_SECRET_KEY`, database credentials, email/API credentials, and other secrets in environment-specific secret stores; never commit `.env` or expose secrets in frontend `VITE_*` variables.
- Set `DEBUG=false` in production and explicitly configure allowed hosts, exact origins, secure cookies, HTTPS, and proxy behavior.
- Rotate credentials through an approved process; use least-privilege database identities and a separate migration identity where appropriate.
- Ensure CI, application logs, error responses, screenshots, and support tickets do not contain secret values.

## Public enquiry endpoint and abuse protection

The anonymous submission endpoint is an abuse and PII boundary:

- Validate type, length, format, active product references, and any required privacy acknowledgement on the server.
- Implemented: five submissions per hour per request IP using a Django REST Framework throttle. It uses the default local-memory cache, which is not shared across app workers/hosts and is not a security-grade distributed limiter. A production shared cache, trusted-proxy/IP review, and edge/WAF control are required before launch.
- The throttle uses a temporary IP-derived cache key; raw IP addresses are not stored with enquiry records. Correct client-IP identification behind production proxies must be configured and reviewed.
- Consider a honeypot and request-size limits. Introduce a CAPTCHA only if abuse demonstrates need and the owner approves the privacy/accessibility tradeoff.
- Make failure messages generic and avoid exposing whether a specific email or business is already known.
- Do not accept file attachments in the initial scope.
- Do not persist raw client IPs by default. If temporary abuse detection needs an IP-derived signal, minimize, pseudonymize, access-control, and expire it under a documented policy.
- Do not log full form bodies or personal data. Restrict enquiry reads to authorized staff and keep internal notes out of public responses.

## Personal information and privacy

Collect only the contact and business information needed to respond to a buyer. The form warns users not to submit sensitive personal/payment details, but no privacy notice or consent acknowledgement is implemented. Before public launch, define and publish data controller/contact details, purposes, lawful basis, retention/deletion process, international transfer/hosting region, and data-subject request handling after jurisdiction is confirmed. Record a notice version/acknowledgement if legally required; do not conflate this with marketing consent. Owner/legal review is required before launch.

## CORS, CSRF and session boundaries

- Prefer same-origin serving for the public website and API.
- If cross-origin requests are required, allow only exact HTTPS frontend origins and avoid permissive wildcard origins with credentials.
- Keep Django CSRF middleware enabled. Preserve CSRF protection for staff session/admin operations.
- The frontend's public JSON submission omits browser credentials/cookies. Admin remains session-authenticated and CSRF-protected. Do not add CSRF exemptions or cross-site cookies as shortcuts.
- Configure trusted origins, secure session/CSRF cookies, HSTS and proxy headers only for the actual reviewed deployment.

## Staff/admin access

- Use individual named staff accounts, strong unique passwords and MFA where available through the chosen identity/control layer.
- Grant staff only the model and action permissions they need; disable or protect unused admin accounts.
- Product image content management is confined to the authenticated admin; model relationships use deletion protection so referenced categories/products cannot be silently removed.
- Restrict admin access through HTTPS and, where feasible, VPN/IP allow-list or identity-aware access control.
- Review access periodically; log sensitive record access/changes without copying enquiry text or credentials into logs.
- Never expose Django admin through a custom public API.

## Database and operations

- Runtime DB credentials should be limited to the SPICEORA schema and required runtime operations; avoid broad global grants.
- Use TLS to remote databases, encrypted backups, least-privilege backup access, patching, monitoring and restore drills.
- Run reviewed migrations as a controlled deployment step; test backup and rollback plans.
- Do not include production personal data in fixtures, screenshots, tests, or development environments.

## Launch security gates

- Test validation and rate limits, authorization boundaries, CSRF/CORS policy, safe error responses, and PII redaction.
- Dependency and static checks; manual review of admin access and deployed security headers/cookie flags.
- Verify backup encryption/restore and enquiry retention/deletion.
- Record operational incident, credential rotation and vulnerability reporting contacts.

Production controls above remain proposals until code/configuration and a real deployed environment demonstrate them.
