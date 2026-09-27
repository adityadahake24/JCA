# Tech Decisions — Offense / Defence

Every open technology and vendor decision on this project, argued both
ways. User-fixed choices (React Native for mobile, a single Python
backend, an SEO-capable web framework) are recorded too, scoped to the
sub-decisions still open within them. This document and the **Tech
Decisions** tab in `JCA_UserStories.xlsx` are generated from the same
source (`stories/decisions.yaml`) and cannot drift from each other.

## Web framework (public web)

**Options considered:** Next.js 15 (App Router) · Remix · SvelteKit · plain Vite SPA

**Offense (case for):** SEO is a hard RFP requirement (§4.1.3, §5.4: meta tags, structured data, sitemap, robots.txt, canonical URLs). Next.js gives SSR + ISR out of the box, server components cut JS payload for elders on older phones, and one app serves both the public site and the signed-in member dashboard described in §3.2 as "a web mirror of the mobile experience."

**Defence (risk / case against):** App Router has real learning-curve cost and a history of breaking changes; deploying on Vercel risks vendor lock-in — mitigated by containerizing with `next start` behind our own reverse proxy on Cloud Run rather than depending on Vercel's platform. A plain Vite SPA is rejected outright: it cannot satisfy the SEO requirement without a separate prerendering layer that duplicates Next.js's job.

**Recommendation:** Next.js 15, App Router, self-hosted on Cloud Run

**Blocks:** S1

---

## Admin utility frontend

**Options considered:** Next.js route group inside the public web app · Separate Vite + React SPA

**Offense (case for):** The admin utility has no SEO need and a completely different UX register — dense tables, a ⌘K command palette, keyboard shortcuts (§4.4.1). A separate Vite SPA gets a faster dev loop, ships to its own subdomain (admin.nyjaincenter.org per §5.4) with independent MFA and optional IP allowlisting, and guarantees admin-only code never leaks into the public bundle members and search engines see.

**Defence (risk / case against):** Two frontend codebases instead of one means duplicated setup and a second build pipeline. Mitigated by sharing `packages/ui` and `packages/tokens` across both apps in the monorepo, so components and design tokens are written once.

**Recommendation:** Separate Vite + React SPA, deployed independently

**Blocks:** S1

---

## Mobile framework *(fixed by user)*

**Options considered:** React Native (Expo, dev client + EAS Build) · React Native (bare workflow)

**Offense (case for):** User has fixed React Native so one codebase covers iOS 17+ and Android 12+ (API 31) without maintaining two native builds, per RFP §1 requirement for feature parity. Expo's managed workflow plus a custom dev client gives config plugins for native modules while keeping EAS Build/Submit for both stores from one pipeline. `expo-updates` can ship copy and content fixes without a store review cycle — real value for a volunteer-run nonprofit that cannot wait a week for an App Store review to fix a typo in a festival date.

**Defence (risk / case against):** Live Darshan requires Picture-in-Picture, AirPlay, and Google Cast (§4.1.2). `react-native-video` v6 and `react-native-google-cast` ship config plugins but require a custom dev client, not Expo Go — meaning the team cannot use the vanilla Expo Go app for daily testing. **Mitigation:** booked as an explicit spike in Sprint 1 (Architecture & Tech Stack) to prove the dev-client build before any feature work depends on it.

**Recommendation:** Expo (managed workflow, custom dev client) + EAS Build/Submit

**Blocks:** S1

---

## Backend framework

**Options considered:** Django 5 + Django REST Framework · FastAPI + SQLAlchemy · Node.js/TypeScript · Go

**Offense (case for):** User has fixed Python; this decision is framework-within-Python. The system is CRUD-and-workflow heavy across ~75 tables and 20 admin sections (§3.4), not compute-heavy. Django's ORM + migrations, built-in auth, and a granular permission model give most of the admin utility's RBAC requirement (§4.4.1) for free. `django-simple-history` covers the immutable 7-year audit log; `django-safedelete` covers the 30-day soft-delete/tombstone requirement; `django-allauth` covers Sign in with Apple/Google. Celery (with the same Postgres-backed broker) handles push fan-out, scheduled publish, and dues-reminder dunning.

**Defence (risk / case against):** DRF serializers are more verbose than FastAPI's Pydantic models, and Django's async story is weaker than FastAPI's native async. This is a real cost on any endpoint that fans out to multiple third-party APIs concurrently (e.g. multi-channel notification delivery) — mitigated by running those specific paths as Celery tasks rather than in-request async code. FastAPI remains the better choice for the Phase 3 AI Chat service, which is a genuinely different, streaming-heavy workload — RFP §4.3 already anticipates a "substantially different technology stack" for that workstream.

**Recommendation:** Django 5 + DRF + drf-spectacular for the core platform; FastAPI reserved for the standalone AI Chat service

**Blocks:** S1

---

## Primary database

**Options considered:** PostgreSQL 16 · MySQL 8 · migrate/extend JCA's existing database

**Offense (case for):** Relational integrity is non-negotiable for money and membership data. Postgres adds JSONB for flexible content blocks (event schedules, quiz questions), `pg_trgm` + `unaccent` for typo-tolerant, diacritic- aware search over Sanskrit/Prakrit terms (§4.4.1), and row-level audit triggers that back the immutable audit log.

**Defence (risk / case against):** RFP §1.1 states a database is "already available," and §3.4 item 15 says "the database of library books is already available." We do not yet know what that system is. **Mitigation:** a dedicated audit and migration-path story is booked in Sprint 2 (Database Schema & Data Model) before the schema is frozen, so existing data is assessed before Postgres is committed to as the system of record.

**Recommendation:** PostgreSQL 16, pending the Sprint 2 legacy-database audit

**Blocks:** S2

---

## Payment processor

**Options considered:** Stripe + PayPal Commerce · Stripe only · Authorize.net · Donorbox/Givebutter hosted widgets

**Offense (case for):** Stripe covers cards, Apple Pay, Google Pay, ACH, and Stripe Billing for recurring giving with pause/edit/cancel in two interactions or fewer (§2.2). Payment Element (web) and the Stripe React Native SDK keep the platform at PCI SAQ-A — card numbers never touch our servers. The Refunds API is idempotent, which fits the two-person-confirmation rule for money (§4.4.1) cleanly: one admin initiates, the second confirms, then the refund call fires once. Stripe offers a reduced processing rate for registered 501(c)(3) nonprofits.

**Defence (risk / case against):** Stripe's own PayPal payment method is not available to US-based Stripe accounts, but §4.1.3 explicitly requires PayPal support — so Stripe alone does not satisfy the RFP. PayPal Commerce Platform is integrated as a second, separate rail specifically for that requirement. **Rejected:** Authorize.net has no clean native-wallet (Apple Pay/Google Pay) story for React Native. Donorbox/Givebutter are rejected because their hosted-widget model can't be embedded natively inside a React Native donation flow and would fork receipts and donation records outside our single source of truth (§2.2). Receipts are generated by our own backend, not by the processor — 501(c)(3) receipts must carry JCA's EIN and "no goods or services were provided" language, which is JCA-specific content no processor template provides. Zelle/bank transfer shown in the mockup is treated as off-platform and recorded via the admin's manual donation-entry component, not as a live payment rail.

**Recommendation:** Stripe (cards, Apple Pay, Google Pay, ACH, Billing) as primary; PayPal Commerce Platform as secondary rail

**Blocks:** S6

---

## Search

**Options considered:** PostgreSQL full-text search + pg_trgm + unaccent · Elasticsearch · Meilisearch (from day one) · Algolia

**Offense (case for):** §4.4.1 requires typo-tolerant search across members, families, donations, events, and posts, including Sanskrit/Prakrit terminology and name transliterations. Postgres FTS with `pg_trgm` (trigram similarity) and `unaccent` (diacritic-insensitive matching) covers this without standing up a second datastore, which keeps Phase 1 infrastructure simpler and the audit surface smaller.

**Defence (risk / case against):** Full-text search over scanned/OCR'd PDF scripture and lecture content in the Phase 2 Library & Jinvani module is exactly the workload Postgres FTS starts to strain under — ranking quality and multi-language stemming are weaker than a dedicated search engine. **Mitigation:** Meilisearch is introduced in Sprint 21, precisely when that workload appears, rather than paying its operational cost from day one for admin/member search Postgres already handles well.

**Recommendation:** Postgres FTS + pg_trgm + unaccent in Phase 1; add Meilisearch in Phase 2 for library/lecture full-text search

**Blocks:** S2

---

## Cloud hosting

**Options considered:** GCP (Cloud Run + Cloud SQL + Cloud Storage/CDN) · AWS (ECS/Fargate + RDS + S3/CloudFront)

**Offense (case for):** Google for Nonprofits offers substantial Cloud credit grants to registered 501(c)(3) organizations — directly relevant to JCA's budget as a nonprofit. Cloud Run's scale-to-zero model suits a congregation-sized traffic pattern with sharp peaks around festivals (Paryushan, Diwali, MJK) and otherwise-quiet weekdays. Cloud Build gives a native CI/CD path matching the team's existing GCP experience.

**Defence (risk / case against):** Cloud Run cold starts add latency on the first request after an idle period — mitigated with a minimum-instance-count of 1 on the API service so the admin utility and payment endpoints never cold-start. AWS ECS/Fargate + RDS + S3/CloudFront is recorded as the equivalent alternative if JCA's board has an existing AWS relationship or credit commitment; the Terraform/IaC layer is written to keep this swap feasible without an application-code rewrite.

**Recommendation:** GCP — Cloud Run, Cloud SQL (Postgres), Cloud Storage + Cloud CDN, Secret Manager, Cloud Build

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

**Offense (case for):** RFP §3.1 requires all four surfaces to share the same design tokens (colors, typography, spacing, radii, shadows). A single `packages/tokens` source of truth — generating CSS custom properties for web/admin and a React Native theme object for mobile from the same token file — satisfies that requirement structurally rather than by convention. A generated TypeScript API client from the OpenAPI schema in `packages/api-client` eliminates drift between backend contract and frontend usage across three separate frontend codebases.

**Defence (risk / case against):** EAS Build needs explicit configuration to build a mobile app that lives inside a monorepo rather than at a repo root — this is booked as a named subtask in Project Setup & CI/CD (Sprint 1) rather than discovered mid-Phase-1.

**Recommendation:** Turborepo + pnpm workspaces: apps/web, apps/admin, apps/mobile, packages/tokens, packages/api-client, packages/validation; backend in services/api

**Blocks:** S1

---

## Localization approach

**Options considered:** Centralized translation catalog in the backend · Per-surface translation files (i18next/next-intl per app, duplicated)

**Offense (case for):** RFP §3.1 explicitly requires localization to be centralized — "strings live in the backend or a shared catalog, not duplicated per surface." A `localization_string` table with a key/locale/value shape, served through the API and cached on each client, gives the admin utility's translator-review workflow (§5.2) a single place to manage English, Hindi, and Gujarati content rather than three.

**Defence (risk / case against):** A backend-served catalog adds a network dependency for strings that per-surface i18next files would resolve at build time — mitigated by aggressive client-side caching of the catalog with a version/ETag check, so steady-state usage never re-fetches unchanged strings.

**Recommendation:** Centralized localization_string table, served via API, cached per client with version-checked invalidation

**Blocks:** S3

---
