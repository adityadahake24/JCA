# Phase & Sprint Roadmap

Relative sprint labelling (no calendar dates) — 2-week cadence,
6-8 person team with parallel surface tracks.

Sprint numbers and week ranges below assume a 6-8 person team running fully parallel surface tracks from Sprint 1. A 3-4 person team cannot run design, backend, web, and mobile in parallel with the same depth: expect Phase 1 to extend from ~19 sprints to ~30-32 sprints (modules become mostly sequential, one or two in flight at a time). A 10-12 person team with a dedicated admin-utility pod can compress Phase 1 to ~14-15 sprints, but coordination overhead and design-review turnaround become the new bottleneck rather than raw implementation capacity.

## Phase 0 — Foundation (Sprints 1–3, Weeks 1–6)

**Goal:** Discovery resolved, design system locked, skeletons deployed, auth working — gates all feature work per RFP §4.1.1.

| Sprint | Weeks | Modules in Flight | Sprint Goal | Complexity | Gate / Demo |
|---|---|---|---|---|---|
| S1 | Weeks 1–2 | UI/UX Design — Mobile, Architecture & Tech Stack, Project Setup & CI/CD, Discovery & Open Items | Kick off design-token extraction, ratify the stack, stand up five empty repos with CI, open every Discovery question. | High | Internal — repo + CI skeleton demo to JCA project committee |
| S2 | Weeks 3–4 | UI/UX Design — Mobile, UI/UX Design — Web & Admin, Database Schema & Data Model, Project Setup & CI/CD, Discovery & Open Items | Lock mobile screens in Figma with the corrected palette; begin web/admin derivation; first schema pass; audit the existing DB JCA mentioned. | Very High | Design review — 28 mobile screens + palette-conflict resolution memo |
| S3 | Weeks 5–6 | UI/UX Design — Web & Admin, API Contract & Integration Map, Project Setup & CI/CD, Auth, Identity & RBAC, Discovery & Open Items | Publish the OpenAPI contract, close all seven RFP §4.6 Discovery items, land Sign in with Apple/Google end-to-end. | High | Phase 0 exit gate — Discovery report + design system + API contract, per RFP §6.1.1 item 1 |

## Phase 1 — v1.0 (initial launch) (Sprints 4–19, Weeks 7–38)

**Goal:** Every P1 feature live on iOS, Android, Web, and Admin. App Store + Play Store approved. Public web launched. RFP §4.1.

| Sprint | Weeks | Modules in Flight | Sprint Goal | Complexity | Gate / Demo |
|---|---|---|---|---|---|
| S4 | Weeks 7–8 | Home & Panchang, Auth, Identity & RBAC | Home dashboard and Panchang live end-to-end on all three member surfaces; auth hardened. | Medium | Sprint demo |
| S5 | Weeks 9–10 | Calendar & Events, Content & Newsletter | Month-grid calendar, event detail + RSVP, and admin-authored announcements/content shipping. | Medium | Sprint demo |
| S6 | Weeks 11–12 | Payments & Billing Infrastructure, Admin — Shell, Dashboards & Members | Stripe + PayPal wired with webhooks and idempotency; admin shell with Member 360 view online. | Very High | Sprint demo — first real charge in staging |
| S7 | Weeks 13–14 | Donations & Causes, Admin — Shell, Dashboards & Members | Causes list, quick-give, event-based prioritization, and Jeev Daya live; admin bulk import complete. | High | Sprint demo |
| S8 | Weeks 15–16 | Recurring Giving & Subscriptions, Membership, Family & Dues | Recurring giving with 2-tap pause/edit/cancel; family records and pending-dues card with Pay All Now. | High | Sprint demo |
| S9 | Weeks 17–18 | Sponsorships & Religious Calendar | Sponsor a Tithi, five-tradition Daily Pooja & Abhishek schedule, Bhojanshala kitchen calendar, Sponsors of the Month. | High | Sprint demo |
| S10 | Weeks 19–20 | Community Feed & Moderation | Whitelist-first community feed with author-only pending state; admin moderation queue with presence indicators. | Medium | Sprint demo |
| S11 | Weeks 21–22 | Notifications & Messaging | APNs/FCM/Web Push/email fan-out live; notification composer with multi-surface preview and segment builder. | High | Sprint demo |
| S12 | Weeks 23–24 | Pathshala, Volunteers & Seva | Children's class hub and volunteer sign-up/hour-logging live on all surfaces. | Medium | Sprint demo |
| S13 | Weeks 25–26 | Live Darshan, Admin — Governance & Operations | Five-tradition HLS player with PiP/AirPlay/Cast; audit log, two-person confirmation, soft-delete trash, feature flags. | Very High | Sprint demo |
| S14 | Weeks 27–28 | Public Web & SEO | Public information pages indexable, structured data, sitemap/robots, unauthenticated donate + newsletter signup. | Medium | Sprint demo |
| S15 | Weeks 29–30 | Localization & Accessibility | Shared translation catalog wired end-to-end; English fully populated; per-surface accessibility audit closed. | Medium | Sprint demo |
| S16 | Weeks 31–32 | Security, Testing & QA | ≥70% business-logic coverage; E2E suite for the five critical flows; dependency scanning in CI. | High | Sprint demo — coverage report |
| S17 | Weeks 33–34 | Security, Testing & QA | Third-party penetration test executed; remediation of High/Critical findings in progress. | High | Pen-test report delivered |
| S18 | Weeks 35–36 | Store & Launch Readiness | Store submission packages assembled; TestFlight + Play Internal Testing distribution; pen-test remediation closed. | Medium | TestFlight / Internal Testing build available to JCA committee |
| S19 | Weeks 37–38 | Store & Launch Readiness | App Store and Google Play approval; public web and admin utility in production. | High | Phase 1 acceptance gate — RFP §6.2, all four surfaces live |

## Phase 2 — v1.5 (should-have follow-on) (Sprints 20–27, Weeks 39–54)

**Goal:** Member-gated content, governance transparency, richer educational resources. Hindi/Gujarati fully populated. RFP §4.2.

| Sprint | Weeks | Modules in Flight | Sprint Goal | Complexity | Gate / Demo |
|---|---|---|---|---|---|
| S20 | Weeks 39–40 | Governance & Documents | Meeting minutes archive (gated, searchable, PDF), JCA Policies, Credits & History. | Medium | Sprint demo |
| S21 | Weeks 41–42 | Library, Jinvani & Lectures | Scripture/lecture catalog with continue-reading state; Meilisearch stood up for full-text PDF search. | High | Sprint demo |
| S22 | Weeks 43–44 | Library, Jinvani & Lectures | Pathshala Books digital library with grade-level browse and parental controls; offline audio download. | Medium | Sprint demo |
| S23 | Weeks 45–46 | Directory, Travel & Facility Booking | Business Directory, Restaurants, Jain Centers USA, and Facility Booking with deposit tracking and conflict view. | Medium | Sprint demo |
| S24 | Weeks 47–48 | Recognition Programs, Youth & YJA | Service Awards nomination flow, Lifetime Supporter Program, Youth section with age-gating. | Medium | Sprint demo |
| S25 | Weeks 49–50 | Past Events & Gallery, Reports & Analytics v2 | Auto-generated Past Events archive; expanded admin reporting (cohort, retention, dues-aging trend). | Medium | Sprint demo |
| S26 | Weeks 51–52 | Hindi & Gujarati Localization | Full Hindi and Gujarati translation populated across all surfaces with reviewer workflow. | Medium | Sprint demo |
| S27 | Weeks 53–54 | v1.5 Hardening & Release | Pen-test refresh for the v1.5 surface area; store updates submitted and approved. | High | Phase 2 acceptance gate — RFP §6.1.2 |

## Phase 3 — v2.0 (nice-to-have, contingent) (Sprints 28–31 (+ parallel AI Chat workstream), Weeks 55–62 (+10 wks AI Chat))

**Goal:** Educational depth and intelligent assistance. Contingent on Phase 1 and Phase 2 acceptance gates. RFP §4.3.

| Sprint | Weeks | Modules in Flight | Sprint Goal | Complexity | Gate / Demo |
|---|---|---|---|---|---|
| S28 | Weeks 55–56 | Jain Philosophy Module | Curriculum structure for anekantvad, ahimsa, syadvad, Nine Tattvas; lesson authoring tools. | Medium | Sprint demo |
| S29 | Weeks 57–58 | Jain Philosophy Module | Progress tracking across the Five Mahavratas and Twelve Vratas modules; full curriculum live. | Medium | Sprint demo |
| S30 | Weeks 59–60 | JCA Cares | Charitable-campaign management integrated with the Causes module for disaster relief and outreach. | Low | Sprint demo |
| S31 | Weeks 61–62 | v2.0 Hardening & Release | Regression pass, updated pen-test scope, store updates for the v2.0 surface area. | Medium | Phase 3 acceptance gate — RFP §6.1.3 (excluding AI Chat) |
| AI-1 | AI Chat Wk 1–2 (parallel to S28-S29) | AI Chat (contingent workstream) | Knowledge-base ingestion pipeline for JCA institutional content; retrieval architecture spike. | High | Internal — architecture review |
| AI-2 | AI Chat Wk 3–4 | AI Chat (contingent workstream) | Guardrail design: doctrine-deferral rules, source citation, escalation triggers. | Very High | Internal — guardrail review with JCA religious advisors |
| AI-3 | AI Chat Wk 5–6 | AI Chat (contingent workstream) | Chat UI on mobile + web; escalation-to-human-staff queue in the admin utility. | High | Sprint demo |
| AI-4 | AI Chat Wk 7–8 | AI Chat (contingent workstream) | Response audit tooling; user-feedback loop; knowledge-base curation UI for admins. | Medium | Sprint demo |
| AI-5 | AI Chat Wk 9–10 | AI Chat (contingent workstream) | Closed pilot with committee members; guardrail tuning; go/no-go for general release. | Medium | AI Chat acceptance gate — separate commission per RFP §6.1.3 item 19 |

## Totals

| Phase | Approx. Duration |
|---|---|
| Phase 0 — Foundation | ~6 weeks |
| Phase 1 — v1.0 (initial launch) | ~32 weeks |
| Phase 2 — v1.5 (should-have follow-on) | ~16 weeks |
| Phase 3 — v2.0 (nice-to-have, contingent) | ~45 weeks |
