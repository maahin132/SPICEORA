# Privacy Policy Framework — UNPUBLISHED — OWNER REVIEW REQUIRED

> **Status: DRAFT / UNPUBLISHED.** This document is a technical framework only. It is not final legal policy, legal advice, a published notice, or owner approval. Do not publish it until the owner supplies and approves every decision identified below.

## Required owner decisions

Before a final privacy policy can be prepared or published, the owner must provide and approve:

1. Legal and display company identity.
2. Privacy jurisdiction and applicable privacy obligations.
3. Data controller identity and responsible entity.
4. Privacy contact channel.
5. Exact policy wording.
6. Personal-data categories collected by the public website and enquiry form.
7. Purpose and legal basis for each processing activity.
8. Hosting and data-location jurisdictions.
9. Email and infrastructure providers used for enquiry data.
10. Cookie and analytics usage, if any.
11. Data-retention period for enquiries, sessions, OTP challenges, logs and backups.
12. Data-deletion and correction procedures.
13. Data-subject rights and request procedure.
14. Any data-sharing or international-transfer disclosures required by law or contract.
15. Staff access, access-control and security responsibility.
16. Policy effective date, review owner and review schedule.

## Current public enquiry data

The existing public enquiry form requests and the existing API accepts the following fields:

- Full name
- Optional company name
- Email address
- Optional telephone number
- Country
- One category or published-product selector
- Estimated quantity and unit
- Optional message

The frontend should not display this framework as a final policy. It should retain the existing truthful notice that privacy and retention details require owner review until the approved policy is supplied.

## Processing boundaries already implemented

- Public enquiries are submitted through the existing anonymous create-only API.
- Public responses return an opaque receipt reference and generic acknowledgement, not internal enquiry details.
- Django Admin is restricted to authorized staff.
- The public API does not expose internal notes or enquiry status.
- OTP values, account passwords and credentials are not included in public responses.
- The existing Gmail configuration is used only for authentication OTP delivery in the implemented authentication flow; this framework does not activate Gmail enquiry notifications.
- This framework does not justify adding mandatory consent fields, consent storage, tracking pixels or analytics.

## Retention framework — unresolved

Retention and deletion periods must not be inferred or asserted. The implementation must not silently backfill retention promises or add consent fields without a documented owner-approved legal requirement.

If a retention period and deletion workflow are approved, they should be documented separately and implemented only after a reviewed change plan.

## Publication checklist

Do not publish a final policy until:

- [ ] Every required owner decision above is documented.
- [ ] Exact legal wording is owner-approved.
- [ ] Actual hosting, database, email and logging providers are named accurately.
- [ ] Retention and deletion behavior matches implementation and backups.
- [ ] Data-subject request channels are genuine and monitored.
- [ ] Cookie or analytics behavior is reviewed and disclosed.
- [ ] The policy review is separately approved.
- [ ] The implementation links the final policy only from the reviewed route.

## Status

**UNPUBLISHED — OWNER REVIEW REQUIRED.** No public privacy route, mandatory consent field, database field, migration or enquiry notification is added by this document.
