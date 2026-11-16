# GENOVA AI — PRD

## Original problem statement
Build a new independent AI platform named GENOVA AI: professional, modular, scalable, focused on genetic inheritance analysis, disease risk, inherited traits and AI scientific explanations. FastAPI backend, genetic engine separate from AI engine, no random numbers, distinguish established calculations from estimates, sources, validation, tests, security, premium subscription architecture, secrets server-side, documentation, GitHub-ready. No diagnostic claims, no invented evidence. Review the 5 legacy repos (aliboozahmad-glitch/baby-gender-*) first, preserve useful features, and never modify the old repos. Work in phases A → B → C with approval.

## User decisions
- Calculations: single-gene, ABO+Rh, disease carrier risk, multi-gene traits (as uncertain estimates)
- AI model: Claude Opus 5.5 (Step B)
- Auth: email + password (Emergent-managed Clerk). First admin: aliboozahmad@gmail.com
- Payments: Stripe, subscribers-only access, monthly + yearly EUR prices set in the admin dashboard (Step C)
- Sex prediction: replaced by real biology (105:100), legacy table not used
- Baby-face generator: premium AI artwork only, never a prediction (Step C)
- Languages: Arabic (RTL), English, German
- Regions: user picks region; regional data stays draft until validated
- Printable PDF reports in AR/EN/DE (Step B)

## Architecture
backend/genova/genetics (pure engine) · genova/i18n · genova/api · genova/auth (roles in Mongo) · genova/ai (Step B, isolated). Frontend React + shadcn, i18n context with RTL. See docs/ARCHITECTURE.md, docs/SCIENCE.md.

## Implemented
- 2026-06 Phase 0: repo audit, feature inventory F1–F17, migration plan, disease panel proposal with link checks (docs/)
- 2026-06 Step A: deterministic engine (Mendelian AD/AR/codominant/incomplete/XR/XD, ABO+Rh exact or ranges, carrier risk for 10 conditions with exact/conditional/validated-population modes, Tanner height, qualitative eye/hair colour, sex ratio). Server-side AR/EN/DE localisation. Clerk auth + roles, owner-scoped history, rate limiting, strict validation, generic errors. Web app: landing, sources (public), dashboard, 6 calculators, history, detail. 85 tests passing (unit, integrity, API, live e2e).

- 2026-06 Code-quality pass: backend complexity refactor (radon: nothing at rank C or worse), frontend complexity ≤8, stable React keys, PropTypes + JSDoc types (src/types.js), usePublic loading/error/retry (LoadState), stale-request guards, Calculate disabled until catalog loads, history summaries + two-step delete. Code review 88 → 95/100. Tests: backend 85/85, frontend jest 8/8. Byte-identical engine output was confirmed across 9,921 inputs.

## Backlog
- P0 (Step B): AI explanation engine (Claude Opus 5.5, guarded); PDF reports AR/EN/DE; full UI polish; Clerk UI localisation
- P0 (Step C): Stripe subscriptions + webhook + server-side gating; admin dashboard (EUR prices, users, data validation status); baby-face AI artwork
- P1: validate regional carrier frequencies (needs the user or a genetic counsellor); family-history Bayesian priors; Down syndrome maternal-age card; manual check of NCBI/CDC/WHO links
- P2: Redis rate limiter; CI workflow; Gulf country-level regions; explicit CORS_ORIGINS allow-list for production; translate history input summaries; ruff style cleanup; frontend tests for async hooks
