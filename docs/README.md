# SPICEORA Documentation Hub

This directory is the technical documentation hub for the SPICEORA project. The repository implementation is authoritative; documents distinguish verified functionality, deployment proposals, and owner decisions that remain pending.

## Project overview

- [Business requirements](./BUSINESS_REQUIREMENTS.md) — implemented journeys, scope boundaries, and owner-confirmation items.
- [Project roadmap](./ROADMAP.md) — completed phases and planned work.
- [Project status](../PROJECT_STATUS.md) — current implementation and release status.
- [Changelog](../CHANGELOG.md) — version and phase history.

## Getting started

- [Developer quickstart](./DEVELOPER_QUICKSTART.md) — local setup commands and environment requirements.
- [Contributing guide](../CONTRIBUTING.md) — repository workflow and verification expectations.
- [Testing guide](./TESTING.md) — automated and manual test commands.
- [Deployment plan](./DEPLOYMENT.md) — release requirements and unresolved infrastructure choices.

## Architecture and data

- [System architecture](./ARCHITECTURE.md) — frontend, backend, authentication, operations, and infrastructure boundaries.
- [Database architecture](./DATABASE.md) — verified models, relationships, constraints, migrations, and inventory rules.
- [API reference](./API.md) — actual public, authentication, customer, and staff endpoint contracts.
- [Authentication](./AUTHENTICATION.md) — registration, OTP, login, recovery, sessions, logout, and permissions.

## Security and operations

- [Security plan](./SECURITY.md) — implemented controls, limitations, secrets, and launch gates.
- [Business workflows](./WORKFLOWS.md) — implemented public, staff, traceability, and inventory workflows.
- [Owner confirmation checklist](./OWNER_CONFIRMATION_CHECKLIST.md) — launch decisions and unknown business information.

## Product and design

- [Information architecture](./INFORMATION_ARCHITECTURE.md) — routes and navigation structure.
- [Design system](./DESIGN_SYSTEM.md) — verified visual and interaction guidance.
- [Product content preparation](./PRODUCT_CONTENT_PREPARATION.md) — owner-controlled product and image intake.
- [Product content CSV template](./product-content-intake-template.csv) — draft prompts; no rows are automatically imported.
- [Privacy policy framework](./PRIVACY_POLICY_FRAMEWORK.md) — unpublished owner-review framework, not an approved policy.

## Documentation conventions

- Use actual Django routes, model fields, serializers, and frontend routes as the source of truth.
- Mark production, deployment, live-provider, browser-session, or owner-confirmed claims only when verified.
- Do not publish company facts, product claims, prices, locations, certifications, or legal policies without approved evidence.
- Keep `.env`, credentials, database dumps, temporary databases, and `mysql_reset.sql` out of documentation and version control.
