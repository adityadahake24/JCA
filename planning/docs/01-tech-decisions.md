# Tech Decisions — Offense / Defence

Every open technology and vendor decision on this project, argued both
ways. User-fixed choices (React Native for mobile, a single Python
backend, an SEO-capable web framework) are recorded too, scoped to the
sub-decisions still open within them. This document and the **Tech
Decisions** tab in `JCA_UserStories.xlsx` are generated from the same
source (`stories/decisions.yaml`) and cannot drift from each other.

## Unified UI framework — Web & App *(fixed by user)*

**Options considered:** Expo (Router + React Native Web), one codebase for iOS/Android/Web · Previous approach: separate Next.js web app + React Native mobile app

**Offense (case for):** User has directed one Expo codebase for every screen — iOS, Android, and web — instead of maintaining a Next.js web app and a React Native mobile app as two separate frontends. Expo Router's file-based routing produces native screens on iOS/Android and a React Native Web build for the browser from the same component tree, so a feature (e.g. Sponsor a Tithi) is built once and ships to all three surfaces instead of twice. EAS Build/Submit already unifies the iOS/Android pipeline; the same pipeline now also produces the web bundle, and `expo-updates` can push copy/content fixes to the app surfaces over the air between store reviews — real value for a volunteer-run nonprofit that cannot wait a week for an App Store review to fix a typo in a festival date.

**Defence (risk / case against):** React Native Web has historically lagged a dedicated SSR framework on the SEO-critical parts of the public site (§4.1.3, §5.4: meta tags, structured data, sitemap, fast first paint on elder devices). **Mitigation:** Expo Router's static/server rendering output mode pre-renders the public web routes (Home, Events, Donate, About, Policies) with real per-page HTML and metadata; the Public Web & SEO module is scoped against this rendering mode from the start, not client-only SPA rendering. Live Darshan's Picture-in-Picture, AirPlay, and Google Cast requirement (§4.1.2) still needs a custom Expo dev client, not the vanilla Expo Go app — booked as the Sprint 1 spike (ARCH-2) before any feature work depends on it.

**Recommendation:** Expo (Router, custom dev client) as the single Web + iOS + Android codebase; EAS Build/Submit for all three targets

**Blocks:** S1

---

## Admin utility & content management *(fixed by user)*

**Options considered:** Payload CMS (self-hosted, Postgres adapter) · Previous approach: separate Vite + React SPA built from scratch

**Offense (case for):** User has directed Payload CMS as the admin and content layer, replacing a bespoke admin SPA. Payload generates a production admin UI — sidebar navigation, list views with sort/filter/search/bulk actions, a document editor, and a Cmd+K jump-to search — directly from a collection config, so most of the RFP's 20 admin sections (§3.4) exist as configuration, not hand-built screens. Per-collection and per-field access control covers a large share of the granular-permissions requirement (§4.4.1). Built-in drafts/versioning and document locking cover much of the audit-trail and concurrent-edit requirements (§4.4.1, §4.5.3) without a custom implementation. Content authored in Payload — announcements, pages, FAQ, policies, translation strings — is exposed over a REST/ GraphQL API the Expo app consumes, which is exactly the "admin can edit everything, including the landing page copy" outcome the user wants.

**Defence (risk / case against):** Payload runs on Node.js/Next.js with its own Postgres adapter — a second server-side stack alongside the Python FastAPI service, a real increase in operational surface versus one backend. **Mitigation:** both services point at the same Postgres 16 instance (Payload owns content/CMS tables, FastAPI owns transactional business tables — money, membership, dues, RSVPs), so there is one database to operate and back up, not two. Screens the RFP needs that don't map onto a generic Payload collection view (Member 360, the Operations Dashboard, the two-person money-confirmation modal, the dues-aging report) are built as custom Payload admin components, keeping exactly one admin application in production rather than a second bespoke app. Payload has no built-in MFA or no-code role editor — both are named as explicitly custom-built work in the Auth & RBAC module rather than assumed free.

**Recommendation:** Payload CMS as the admin utility and content layer, self-hosted, Postgres adapter, custom admin views for the screens a generic collection view can't express

**Blocks:** S1

---

## Backend framework *(fixed by user)*

**Options considered:** FastAPI + SQLAlchemy + Pydantic (Python) · Previous approach: Django 5 + Django REST Framework

**Offense (case for):** User has directed FastAPI as the single backend framework, replacing the earlier Django/DRF plan. FastAPI generates the OpenAPI 3.1 schema natively from route and Pydantic-model type hints — no separate schema-generation library needed — which keeps the packages/api-client codegen pipeline simple. Native async support fits notification fan-out (APNs/FCM/Web Push/email), concurrent payment-processor webhooks (Stripe + PayPal), and the Phase 3 AI Chat streaming workload on the same stack the rest of the platform already runs, rather than reserving a second, "substantially different" stack for that one workstream as previously planned — RFP §4.3's anticipated stack difference is now just "the same FastAPI service, a different workload."

**Defence (risk / case against):** FastAPI doesn't bundle Django's batteries — no built-in ORM, admin site, auth system, or migrations tool. **Mitigation:** SQLAlchemy 2.x is the ORM, Alembic handles migrations, and a small shared base-model mixin (id, created/updated timestamps, actor tracking, soft-delete flag, optimistic-lock version column) plus one audit-log table replace what django-safedelete/django-simple-history gave for free — this is booked as its own story (DB-2) rather than assumed to come with the framework. The admin-site gap is filled entirely by Payload CMS (above), so FastAPI never needs one of its own. Celery (or an RQ-based equivalent) still handles push fan-out, scheduled publish, and dues-reminder dunning as background jobs outside the request cycle.

**Recommendation:** FastAPI + SQLAlchemy 2.x + Alembic + Pydantic for the core platform API and the Phase 3 AI Chat service — one Python backend throughout

**Blocks:** S1

---

## Primary database

**Options considered:** PostgreSQL 16 · MySQL 8 · migrate/extend JCA's existing database

**Offense (case for):** Relational integrity is non-negotiable for money and membership data. Postgres adds JSONB for flexible content blocks (event schedules, quiz questions), `pg_trgm` + `unaccent` for typo-tolerant, diacritic-aware search over Sanskrit/Prakrit terms (§4.4.1), and row-level audit triggers that back the immutable audit log. Both the FastAPI service and Payload CMS target this same Postgres instance, in separate schemas, so there is one datastore to provision, back up, and monitor.

**Defence (risk / case against):** RFP §1.1 states a database is "already available," and §3.4 item 15 says "the database of library books is already available." We do not yet know what that system is. **Mitigation:** a dedicated audit and migration-path story is booked in the Data Migration Planning module before the schema is frozen, so existing data is assessed before Postgres is committed to as the system of record.

**Recommendation:** PostgreSQL 16, pending the Phase 0 legacy-database audit

**Blocks:** S2

---

## Payment processor

**Options considered:** Stripe + PayPal Commerce · Stripe only · Authorize.net · Donorbox/Givebutter hosted widgets

**Offense (case for):** Stripe covers cards, Apple Pay, Google Pay, ACH, and Stripe Billing for recurring giving with pause/edit/cancel in two interactions or fewer (§2.2). Payment Element (web) and the Stripe React Native SDK keep the platform at PCI SAQ-A — card numbers never touch our servers. The Refunds API is idempotent, which fits the two-person-confirmation rule for money (§4.4.1) cleanly: one admin initiates, the second confirms, then the refund call fires once. Stripe offers a reduced processing rate for registered 501(c)(3) nonprofits.

**Defence (risk / case against):** Stripe's own PayPal payment method is not available to US-based Stripe accounts, but §4.1.3 explicitly requires PayPal support — so Stripe alone does not satisfy the RFP. PayPal Commerce Platform is integrated as a second, separate rail specifically for that requirement. **Rejected:** Authorize.net has no clean native-wallet (Apple Pay/Google Pay) story for a React Native app. Donorbox/ Givebutter are rejected because their hosted-widget model can't be embedded natively inside the Expo app's donation flow and would fork receipts and donation records outside our single source of truth (§2.2). Receipts are generated by our own backend, not by the processor — 501(c)(3) receipts must carry JCA's EIN and "no goods or services were provided" language, which is JCA-specific content no processor template provides. Zelle/bank transfer shown in the mockup is treated as off-platform and recorded via the admin's manual donation-entry component, not as a live payment rail.

**Recommendation:** Stripe (cards, Apple Pay, Google Pay, ACH, Billing) as primary; PayPal Commerce Platform as secondary rail

**Blocks:** S6

---

## Search

**Options considered:** PostgreSQL full-text search + pg_trgm + unaccent · Elasticsearch · Meilisearch (from day one) · Algolia

**Offense (case for):** §4.4.1 requires typo-tolerant search across members, families, donations, events, and posts, including Sanskrit/Prakrit terminology and name transliterations. Postgres FTS with `pg_trgm` (trigram similarity) and `unaccent` (diacritic-insensitive matching) covers this without standing up a second datastore, which keeps Phase 1 infrastructure simpler and the audit surface smaller.

**Defence (risk / case against):** Full-text search over scanned/OCR'd PDF scripture and lecture content in the Phase 2 Library & Jinvani module is exactly the workload Postgres FTS starts to strain under — ranking quality and multi-language stemming are weaker than a dedicated search engine. **Mitigation:** Meilisearch is introduced in Phase 2, precisely when that workload appears, rather than paying its operational cost from day one for admin/member search Postgres already handles well.

**Recommendation:** Postgres FTS + pg_trgm + unaccent in Phase 1; add Meilisearch in Phase 2 for library/lecture full-text search

**Blocks:** S2

---

## Cloud hosting

**Options considered:** GCP (Cloud Run + Cloud SQL + Cloud Storage/CDN) · AWS (ECS/Fargate + RDS + S3/CloudFront)

**Offense (case for):** Google for Nonprofits offers substantial Cloud credit grants to registered 501(c)(3) organizations — directly relevant to JCA's budget as a nonprofit. Cloud Run's scale-to-zero model suits a congregation-sized traffic pattern with sharp peaks around festivals (Paryushan, Diwali, MJK) and otherwise-quiet weekdays, and hosts the FastAPI service and the Payload admin/CMS app as two independent Cloud Run services against the same Cloud SQL instance. Cloud Build gives a native CI/CD path matching the team's existing GCP experience.

**Defence (risk / case against):** Cloud Run cold starts add latency on the first request after an idle period — mitigated with a minimum-instance-count of 1 on both the FastAPI service and the Payload admin service so the admin utility and payment endpoints never cold-start. AWS ECS/Fargate + RDS + S3/CloudFront is recorded as the equivalent alternative if JCA's board has an existing AWS relationship or credit commitment; the Terraform/ IaC layer is written to keep this swap feasible without an application-code rewrite.

**Recommendation:** GCP — Cloud Run (FastAPI + Payload), Cloud SQL (Postgres), Cloud Storage + Cloud CDN, Secret Manager, Cloud Build

**Blocks:** S1

---

## Live Darshan streaming

**Options considered:** Player only, JCA-supplied HLS URLs · Fully managed live encoding (Mux / Cloudflare Stream Live)

**Offense (case for):** RFP §3.4 item 14 scopes the admin's job as configuring stream-source URLs per tradition (HLS URLs, fallback, scheduled on/off windows) and monitoring stream health — not operating an encoder. Building only the player, PiP, AirPlay/Cast, and health-check layer keeps several sprints of encoding infrastructure out of scope that the RFP never asked for.

**Defence (risk / case against):** If JCA does not already have a hardware or software encoder producing HLS streams from the five shrines, this decision assumes infrastructure that may not exist. **Mitigation:** this is flagged as a Discovery question (see Discovery & Open Items) — if JCA has no encoder, a managed live-encoding service becomes a separately-priced change order, not silent scope creep absorbed into Phase 1.

**Recommendation:** Player only in Phase 1; managed encoding is a change order if Discovery reveals JCA has no encoder

**Blocks:** S1

---

## Monorepo tooling

**Options considered:** Turborepo + pnpm workspaces · Nx · separate repos per surface

**Offense (case for):** RFP §3.1 requires every surface to share the same design tokens (colors, typography, spacing, radii, shadows). A single `packages/tokens` source of truth — generating CSS custom properties for the Payload admin theme and a React Native theme object for the Expo app from the same token file — satisfies that requirement structurally rather than by convention. A generated TypeScript API client from FastAPI's OpenAPI schema in `packages/api-client` eliminates drift between the backend contract and the Expo app's usage of it.

**Defence (risk / case against):** EAS Build needs explicit configuration to build an Expo app that lives inside a monorepo rather than at a repo root — this is booked as a named subtask in Project Setup & CI/CD (Sprint 1) rather than discovered mid-Phase-1. Payload's own Next.js app also needs to be told where the monorepo's shared packages live.

**Recommendation:** Turborepo + pnpm workspaces: apps/expo (Web + iOS + Android), apps/admin (Payload CMS), packages/tokens, packages/ui, packages/api-client; backend in services/api (FastAPI)

**Blocks:** S1

---

## Localization approach

**Options considered:** Centralized LocalizationStrings collection in Payload · Per-surface translation files (i18next per app, duplicated)

**Offense (case for):** RFP §3.1 explicitly requires localization to be centralized — "strings live in the backend or a shared catalog, not duplicated per surface." A `LocalizationStrings` collection in Payload, with English/Hindi/ Gujarati fields per key, gives the admin utility's translator-review workflow (§5.2) a native fit: Payload's draft/publish and versioning already model "submitted, pending review, live" for a string, rather than a separate review workflow built from scratch.

**Defence (risk / case against):** A Payload-served catalog adds a network dependency for strings that per-surface i18next files would resolve at build time — mitigated by aggressive client-side caching of the catalog in the Expo app with a version/ETag check, so steady-state usage never re-fetches unchanged strings.

**Recommendation:** Centralized LocalizationStrings collection in Payload, served via its API, cached in the Expo app with version-checked invalidation

**Blocks:** S3

---
