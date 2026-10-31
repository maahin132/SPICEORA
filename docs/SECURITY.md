# Security Plan

## Scope and implementation status

This document defines current controls and remaining launch requirements. It is not a security certification. The current code has environment-based Django settings, explicit development CORS configuration, Django's standard middleware, a public health endpoint, read-only catalogue endpoints, and a public enquiry-create endpoint. Production deployment controls and a verified security review are not implemented.

The anonymous catalogue API returns only products marked published and belonging to active categories. The category list exposes active owner-provided labels for selection, without asserting availability. Product detail returns 404 for missing, unpublished, or inactive-category products. Admin is the only catalogue write surface and uses Django's authenticated, CSRF-protected session admin.

Product image uploads are available only through authenticated Django Admin. Server-side validation accepts matching JPG/JPEG, PNG, or WebP content and extensions; limits files to 5 MiB, 8,000 px per side, and 40 megapixels; and gives new uploads random UUID filenames under `products/`. Alternative text is required when an image is supplied. Old files are not automatically removed on image replacement/removal. Development uploads are served by Django only in DEBUG mode. Production media hosting, malware/content scanning, and CDN policy are not implemented and must be designed before production uploads are enabled. These checks do not replace production storage isolation, content scanning, or safe response headers.

The Phase 6 intake CSV is documentation, not application input: it is not automatically imported, does not create products, and optional unverified claims must not be copied into public records without evidence and owner approval. Do not put credentials or buyer personal information in the intake file.

The public enquiry endpoint stores submitted contact/business data and returns a generic receipt reference. Server-side validation enforces required fields, bounds, category/product visibility, and quantity-unit pairing. The public response does not return enquiry details, status, or internal notes. No email or other notification provider is configured.

Phase 7 farm, crop season, harvest, batch, processing and inventory data are private operational records. They are available through authenticated Django Admin and `/api/v1/operations/` staff collections only. API access requires a staff user plus per-model view/add permissions; unsafe session-authenticated requests retain CSRF protection. Correction movements require the additional `approve_inventory_correction` model permission. There are no anonymous operations reads, public write endpoints, or operations routes in the React site. Internal notes and document references are not serialized by public catalogue/enquiry endpoints.

Phase 10 adds a custom React staff enquiry inbox and detail page. The API remains protected by Django session authentication, `IsAdminUser`, model-level view/change permissions, and CSRF on writes. The inbox minimizes personal-data exposure; email, phone, message, and internal notes are returned only by the staff detail API. Search does not index email or phone. The PATCH contract accepts only status and internal notes, supports only four existing statuses, and has no dashboard/delete operation. React route guards are navigation aids only; backend permission and CSRF enforcement remain authoritative. Django Admin remains available, and enquiry deletion is disabled.

Phase 8 adds customer accounts and a protected operations React interface. The standard Django user model is retained. Public registration creates inactive non-staff users and has no writable privilege fields; successful email verification activates a customer account. Mobile numbers are validated and stored, but explicitly remain unverified; no SMS is sent and no mobile login or SMS recovery is allowed. Staff login is separate, and each operations API route enforces the existing `is_staff` boundary plus its Django model permission. Frontend route guards improve navigation only and are not an authorization control.

OTP codes are generated with Python's cryptographically secure random source, six digits long, stored only as Django password hashes, expire after five minutes, permit at most five incorrect attempts, and cannot be reused. Resends rotate codes and enforce a 60-second cooldown. DRF throttles apply per IP and an additional hashed account-identity throttle; the default local-memory cache is not suitable for distributed production throttling. Email account recovery uses a generic response that does not identify whether the submitted email exists. Registration also returns the same HTTP 201 status and response structure for valid new and duplicate email/mobile submissions. A duplicate gets a random, non-persisted challenge identifier; no account or challenge is created and no OTP is sent. Database uniqueness constraints remain in place for races. Registration responses have a one-second minimum duration to reduce fast-path timing differences; synchronous SMTP can exceed that floor, so this is not constant-time protection. SMS recovery is rejected. Password reset requires verified email OTP and invalidates matching Django sessions.

Session cookies are HTTP-only and same-site defaults to `Lax`; secure cookies default on when `DEBUG=false`. CSRF initialization returns a request token to the browser, which holds it in memory only and sends it in `X-CSRFToken`. The frontend never stores passwords, OTPs, CSRF values, or session IDs in localStorage. Same-origin HTTPS is preferred; if deploying cross-site origins, configure exact CORS/CSRF trusted origins, secure cookies, and `SameSite=None` only with HTTPS.

OTP delivery is restricted in code to Gmail SMTP at `smtp.gmail.com:587` with TLS. It requires `EMAIL_PROVIDER=gmail`, the full Gmail address as `GOOGLE_SMTP_LOGIN` and `DEFAULT_FROM_EMAIL`, and a Google App Password in `GOOGLE_SMTP_APP_PASSWORD`; the regular Google password is never used. Google requires 2-Step Verification for App Passwords and may restrict their availability. Missing, mismatched, or failing settings fail closed; SMTP errors return a safe message and no OTP or credentials are logged or included in responses. The configured backend cannot fall back to another provider. This personal Gmail option is intended only for low-volume testing and is not a production transactional delivery guarantee; Google can apply limits or block suspicious use. SMS delivery is unavailable: the SMS adapter rejects delivery and makes no network call. Provider readiness is not proof of actual delivery. No real email delivery is claimed until an owner-approved inbox receives a test OTP.

Processing records and inventory movements are append-only in model/admin/API paths. Batch origin/identity/initial quantity are immutable, and farm/season/harvest relationships use protected foreign keys and admin deletion restrictions. Inventory writes lock the batch row and reject reservations/outflows that would make available stock negative; production batch creation and its initial receipt are transactional. This is application-level workflow protection, not tamper-proof ledger storage: database administrators can still alter rows, and database auditing/backup/restore controls remain deployment responsibilities.

## Secrets and configuration

- Keep `DJANGO_SECRET_KEY`, database credentials, `GOOGLE_SMTP_LOGIN`, and `GOOGLE_SMTP_APP_PASSWORD` in environment-specific secret stores; never commit `.env` or expose secrets in frontend `VITE_*` variables. Revoke the App Password if it is no longer needed or suspected exposed.
- Django startup now fails with `ImproperlyConfigured` if `DJANGO_SECRET_KEY` is missing/empty or still equals the `.env.example` placeholder. This prevents starting with the documented placeholder; deployments must inject a unique secret.
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
- The public enquiry JSON submission omits browser credentials/cookies. Authentication/operations requests use session cookies and CSRF tokens, with credentials enabled only for the exact configured origins. Do not add CSRF exemptions or cross-site cookies as shortcuts.
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
