# API Contract & Integration Map

Representative endpoints per module (not exhaustive of every route),
each traced to the tables it touches, the surfaces that call it, the
minimum role required, and the story that specifies it. The full
contract is published as OpenAPI 3.1 via drf-spectacular
(see `API-1` in the API Contract & Integration Map module).

**Versioning:** all routes are prefixed `/api/v1/`. Breaking changes
require a minimum 90-day deprecation window with a `Sunset` header
(see decision `API-3`).

| Endpoint | Method | Tables Read | Tables Written | Surfaces | Min Role | Phase | Story |
|---|---|---|---|---|---|---|---|
| `/api/v1/auth/sign-in` | POST | user, auth_identity | session, audit_log | iOS, Android, Web | Guest | phase0 | AUTH-1 |
| `/api/v1/auth/register` | POST | user | user, member_profile, family, family_member, audit_log | iOS, Android, Web | Guest | phase0 | AUTH-2 |
| `/api/v1/auth/mfa/enroll` | POST | user | mfa_factor, audit_log | Admin, iOS, Android, Web | Member | phase0 | AUTH-4 |
| `/api/v1/admin/roles` | GET, POST, PATCH | role, permission, role_permission | role, role_permission, audit_log | Admin | Super-Admin | phase0 | AUTH-6 |
| `/api/v1/panchang/today` | GET | —  (computed/configured, no dedicated table; source config only) | — | iOS, Android, Web | Guest | phase1 | HP-2 |
| `/api/v1/home/dashboard` | GET | thought_of_day, quiz_question, event, post, member_profile | — | iOS, Android, Web | Guest | phase1 | HP-1 |
| `/api/v1/quiz/today/attempt` | POST | quiz_question | quiz_attempt | iOS, Android, Web | Member | phase1 | HP-4 |
| `/api/v1/events` | GET | event, event_category, event_schedule_block | — | iOS, Android, Web | Guest | phase1 | CAL-1 |
| `/api/v1/events/{id}/rsvp` | POST, DELETE | event, rsvp | rsvp, audit_log | iOS, Android, Web | Member | phase1 | CAL-3 |
| `/api/v1/admin/events` | GET, POST, PATCH, DELETE | event, event_schedule_block, event_sponsorship_tier | event, event_schedule_block, event_sponsorship_tier, audit_log, tombstone | Admin | Committee Member | phase1 | CAL-4 |
| `/api/v1/admin/calendar/conflicts` | GET | event, pooja_slot, facility_booking | — | Admin | Committee Member | phase1 | CAL-5 |
| `/api/v1/admin/content/announcements` | GET, POST, PATCH | announcement, segment | announcement, notification_campaign, audit_log | Admin | Committee Member | phase1 | CN-1 |
| `/api/v1/newsletter/subscribe` | POST | — | localization_string (n/a), segment (subscriber list) | Web | Guest | phase1 | CN-6 |
| `/api/v1/payments/intent` | POST | payment_method | payment_transaction, audit_log | iOS, Android, Web | Guest | phase1 | PAY-1 |
| `/api/v1/payments/paypal/order` | POST | — | payment_transaction, audit_log | iOS, Android, Web | Guest | phase1 | PAY-2 |
| `/api/v1/admin/refunds` | POST | payment_transaction | refund, audit_log | Admin | Admin (money permission, two-actor) | phase1 | PAY-6 |
| `/api/v1/receipts/{donation_id}` | GET | donation, receipt | receipt (on first generation) | iOS, Android, Web | Member | phase1 | PAY-5 |
| `/api/v1/admin/members/{id}/360` | GET | member_profile, family, membership, dues_ledger_entry, donation, volunteer_hour_log, enrollment, rsvp, post, session | — | Admin | Committee Member | phase1 | ADM-4 |
| `/api/v1/admin/members/import` | POST | — | user, member_profile, family, family_member, audit_log | Admin | Admin | phase1 | ADM-5 |
| `/api/v1/causes` | GET | cause, event | — | iOS, Android, Web | Guest | phase1 | DON-1 |
| `/api/v1/donations` | POST | cause | donation, donation_allocation, payment_transaction, receipt, audit_log | iOS, Android, Web | Guest | phase1 | DON-2 |
| `/api/v1/donations/history` | GET | donation, receipt, year_end_statement | — | iOS, Android, Web | Member | phase1 | DON-5 |
| `/api/v1/admin/causes` | GET, POST, PATCH, DELETE | cause | cause, audit_log, tombstone | Admin | Committee Member | phase1 | DON-6 |
| `/api/v1/subscriptions` | GET, POST | recurring_subscription | recurring_subscription, payment_method, audit_log | iOS, Android, Web | Member | phase1 | SUB-1 |
| `/api/v1/subscriptions/{id}` | PATCH, DELETE | recurring_subscription | recurring_subscription, audit_log | iOS, Android, Web | Member | phase1 | SUB-2 |
| `/api/v1/admin/subscriptions/{id}/cancel` | POST | recurring_subscription | recurring_subscription, audit_log | Admin | Admin (money permission, two-actor) | phase1 | SUB-5 |
| `/api/v1/families/{id}` | GET, PATCH | family, family_member | family, family_member, audit_log | iOS, Android, Web | Family Primary | phase1 | MFD-1 |
| `/api/v1/families/{id}/dues` | GET | dues_item, dues_ledger_entry | — | iOS, Android, Web | Family Primary | phase1 | MFD-2 |
| `/api/v1/families/{id}/dues/pay-all` | POST | dues_item | payment_transaction, dues_ledger_entry, audit_log | iOS, Android, Web | Family Primary | phase1 | MFD-2 |
| `/api/v1/admin/families/merge` | POST | family, family_member, donation, dues_ledger_entry | family, family_member, audit_log, tombstone | Admin | Admin | phase1 | MFD-4 |
| `/api/v1/admin/dues/credit` | POST | dues_item | dues_ledger_entry, audit_log | Admin | Admin (money permission, two-actor) | phase1 | MFD-6 |
| `/api/v1/tithis/available` | GET | tithi_slot | — | iOS, Android, Web | Guest | phase1 | SPN-1 |
| `/api/v1/sponsorships` | POST | tithi_slot, pooja_slot, bhojanshala_slot | sponsorship, donation, audit_log | iOS, Android, Web | Guest | phase1 | SPN-1 |
| `/api/v1/religious-calendar/pooja` | GET | pooja_slot, tradition | — | iOS, Android, Web | Guest | phase1 | SPN-2 |
| `/api/v1/admin/religious-calendar/pooja` | POST, PATCH | pooja_slot | pooja_slot, audit_log | Admin | Committee Member | phase1 | SPN-5 |
| `/api/v1/community/posts` | GET, POST | post, post_media, post_reaction, badge | post, post_media, audit_log | iOS, Android, Web | Guest (read), Member (post) | phase1 | COM-2 |
| `/api/v1/community/posts/{id}/report` | POST | post | content_report | iOS, Android, Web | Member | phase1 | COM-3 |
| `/api/v1/admin/moderation/queue` | GET | post, content_report | — | Admin | Committee Member | phase1 | COM-4 |
| `/api/v1/admin/moderation/{post_id}/decision` | POST | post | post, moderation_action, audit_log | Admin | Committee Member | phase1 | COM-4 |
| `/api/v1/devices/register` | POST | — | device_token | iOS, Android, Web | Guest | phase1 | NOT-2 |
| `/api/v1/notifications/preferences` | GET, PATCH | notification_preference | notification_preference | iOS, Android, Web | Member | phase1 | NOT-2 |
| `/api/v1/admin/notifications/campaigns` | GET, POST | notification_template, segment | notification_campaign, audit_log | Admin | Committee Member | phase1 | NOT-3 |
| `/api/v1/admin/segments` | GET, POST | segment | segment | Admin | Committee Member | phase1 | NOT-4 |
| `/api/v1/admin/notifications/{id}/delivery-report` | GET | delivery_receipt | — | Admin | Committee Member | phase1 | NOT-5 |
| `/api/v1/pathshala/my-children` | GET | family_member, enrollment, pathshala_class, lesson | — | iOS, Android, Web | Pathshala Parent | phase1 | PS-1 |
| `/api/v1/admin/pathshala/enrollments` | GET, POST, PATCH | enrollment, pathshala_class | enrollment, audit_log | Admin | Committee Member | phase1 | PS-3 |
| `/api/v1/volunteer/opportunities` | GET | volunteer_opportunity | — | iOS, Android, Web | Guest | phase1 | VOL-1 |
| `/api/v1/volunteer/opportunities/{id}/signup` | POST | volunteer_opportunity | volunteer_signup | iOS, Android, Web | Member | phase1 | VOL-1 |
| `/api/v1/admin/volunteer/hours` | POST | — | volunteer_hour_log, audit_log | Admin | Committee Member | phase1 | VOL-3 |
| `/api/v1/live-darshan/streams` | GET | tradition (stream config, not modeled as its own table in v1) | — | iOS, Android, Web | Guest | phase1 | LD-1 |
| `/api/v1/admin/live-darshan/streams/{tradition_id}` | PATCH | tradition | integration_credential (stream URL ref), audit_log | Admin | Admin | phase1 | LD-4 |
| `/api/v1/admin/audit-log` | GET | audit_log | — | Admin | Super-Admin | phase1 | GOV-1 |
| `/api/v1/admin/confirmations/{id}/confirm` | POST | —  (transient confirmation request, not a persisted table) | audit_log (both actors) | Admin | Admin (second actor) | phase1 | GOV-2 |
| `/api/v1/admin/trash/{table}` | GET, POST (restore) | tombstone | tombstone, audit_log | Admin | Admin | phase1 | GOV-3 |
| `/api/v1/admin/feature-flags` | GET, PATCH | feature_flag | feature_flag, audit_log | Admin | Super-Admin | phase1 | GOV-4 |
| `/api/v1/admin/credentials-vault` | GET, POST | integration_credential | integration_credential, audit_log | Admin | Super-Admin | phase1 | GOV-6 |
| `/api/v1/public/pages/{slug}` | GET | page | — | Web | Guest | phase1 | SEO-1 |
| `/api/v1/localization/catalog` | GET | localization_string | — | iOS, Android, Web, Admin | Guest | phase0 | L10N-1 |
| `/api/v1/admin/localization/catalog` | PATCH | localization_string | localization_string, audit_log | Admin | Committee Member | phase1 | L10N-5 |
| `/api/v1/account/delete` | POST | user, donation | user (tombstoned/anonymized), donation (de-linked), audit_log | iOS, Android, Web | Member | phase1 | SEC-6 |
| `/api/v1/governance/minutes` | GET | meeting_minute | — | iOS, Android, Web | Member (tier-gated) | phase2 | GOVD-1 |
| `/api/v1/admin/governance/minutes` | POST, PATCH | meeting_minute | meeting_minute, audit_log | Admin | Committee Member | phase2 | GOVD-2 |
| `/api/v1/library/search` | GET | media_asset (Meilisearch index of catalog content) | — | iOS, Android, Web | Guest | phase2 | LIB-1 |
| `/api/v1/pathshala-books/{grade}` | GET | media_asset, enrollment | — | iOS, Android, Web | Pathshala Parent | phase2 | LIB-5 |
| `/api/v1/directory/businesses` | GET, POST (submit listing) | —  (business_listing table, extension of media_asset+content pattern) | — | iOS, Android, Web | Guest (read), Member (submit) | phase2 | DIR-1 |
| `/api/v1/facilities/{id}/book` | POST | facility, facility_booking | facility_booking, payment_transaction, audit_log | iOS, Android, Web | Member | phase2 | DIR-3 |
| `/api/v1/admin/facility-bookings/{id}/decision` | POST | facility_booking | facility_booking, audit_log | Admin | Committee Member | phase2 | DIR-4 |
| `/api/v1/service-awards/nominate` | POST | — | service_award | iOS, Android, Web | Member | phase2 | REC-1 |
| `/api/v1/admin/reports/donor-cohort` | GET | donation, member_profile | — | Admin | Admin (Treasurer) | phase2 | RPT-1 |
| `/api/v1/admin/localization/hi-gu/{key}` | PATCH | localization_string | localization_string, audit_log | Admin | Committee Member | phase2 | L10N2-1 |
| `/api/v1/education/philosophy/tracks` | GET | —  (curriculum_track/lesson, Phase 3 addition to Education & Seva domain) | — | iOS, Android, Web | Member | phase3 | PHIL-1 |
| `/api/v1/chat/message` | POST | —  (knowledge-base index, separate AI Chat service) | —  (conversation log in the AI Chat service's own store) | iOS, Android, Web | Member | phase3 | AI-C-3 |
| `/api/v1/admin/chat/escalations` | GET | —  (AI Chat service escalation store) | — | Admin | Committee Member | phase3 | AI-C-4 |
