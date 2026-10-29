# Security Plan

## Scope and implementation status

This document defines requirements for later business functionality. It is not a security certification. The current code is a development foundation: it has environment-based Django settings, explicit development CORS configuration, Django's standard middleware, and a public health endpoint. It does **not** yet implement product/enquiry APIs, public-form abuse controls, staff operational policy, production deployment controls, or a verified security review.

The Phase 2 homepage's enquiry section is a non-submitting placeholder; it does not collect personal information. Enquiry privacy and abuse controls are future launch requirements, not present controls.

## Secrets and configuration

- Keep `DJANGO_SECRET_KEY`, database credentials, email/API credentials, and other secrets in environment-specific secret stores; never commit `.env` or expose secrets in frontend `VITE_*` variables.
- Set `DEBUG=false` in production and explicitly configure allowed hosts, exact origins, secure cookies, HTTPS, and proxy behavior.
- Rotate credentials through an approved process; use least-privilege database identities and a separate migration identity where appropriate.
- Ensure CI, application logs, error responses, screenshots, and support tickets do not contain secret values.

## Public enquiry endpoint — requirements

The proposed anonymous enquiry submission endpoint is an abuse and PII boundary:

- Validate type, length, format, active product references, and any required privacy acknowledgement on the server.
- Use a configurable rate limit at the edge/WAF or reverse proxy and a compatible application-level limit. DRF's simple throttles alone are not a security-grade distributed limiter. Tune limits against real traffic and false-positive risk; do not claim a threshold exists until implemented and tested.
- Consider a honeypot and request-size limits. Introduce a CAPTCHA only if abuse demonstrates need and the owner approves the privacy/accessibility tradeoff.
- Make failure messages generic and avoid exposing whether a specific email or business is already known.
- Do not accept file attachments in the initial scope.
- Do not persist raw client IPs by default. If temporary abuse detection needs an IP-derived signal, minimize, pseudonymize, access-control, and expire it under a documented policy.
- Do not log full form bodies or personal data. Restrict enquiry reads to authorized staff and keep internal notes out of public responses.

## Personal information and privacy

Collect only the contact and business information needed to respond to a buyer. Publish a privacy notice before accepting submissions, define data controller/contact details, purposes, lawful basis, retention and deletion process, international transfer/hosting region, and data-subject request handling after jurisdiction is confirmed. Record a notice version/acknowledgement if legally required; do not conflate this with marketing consent. Owner/legal review is required before launch.

## CORS, CSRF and session boundaries

- Prefer same-origin serving for the public website and API.
- If cross-origin requests are required, allow only exact HTTPS frontend origins and avoid permissive wildcard origins with credentials.
- Keep Django CSRF middleware enabled. Preserve CSRF protection for staff session/admin operations.
- Keep anonymous public API submissions cookie-less and unauthenticated unless a reviewed design says otherwise. Do not add CSRF exemptions or cross-site cookies as shortcuts.
- Configure trusted origins, secure session/CSRF cookies, HSTS and proxy headers only for the actual reviewed deployment.

## Staff/admin access

- Use individual named staff accounts, strong unique passwords and MFA where available through the chosen identity/control layer.
- Grant staff only the model and action permissions they need; disable or protect unused admin accounts.
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

All implementation and deployment controls above remain proposals until code/configuration and a real deployed environment demonstrate them.
