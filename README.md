# GENOVA AI

Genetic inheritance analysis with a deterministic, source-referenced calculation engine.
Educational use only. GENOVA AI does not provide medical diagnoses.

**Status: Step A (calculation engine, tests, authentication, basic web app).**
Steps B (AI explanations, full UI, PDF reports) and C (subscriptions, admin, baby-face artwork) haven't started yet.

## Stack
- Backend: Python FastAPI (`backend/`), MongoDB (Motor)
- Frontend: React + Tailwind + shadcn/ui (`frontend/`), Arabic (RTL) / English / German
- Auth: Emergent-managed Clerk (email + password), verified server-side on every request

## Layout
```
backend/
  server.py                 app wiring, error handlers, CORS, security headers
  clerk_auth.py             Clerk session verification
  genova/
    genetics/               PURE calculation engine: no I/O, no AI, no randomness
      core.py               Fraction-based Punnett helper + result format
      mendelian.py          AD, AR, codominant, incomplete, X-linked recessive/dominant
      blood_type.py         ABO + RhD, exact or ranges across compatible genotypes
      carrier_risk.py       10-condition panel; exact, conditional, or validated population estimate
      polygenic.py          Tanner mid-parental height; qualitative eye/hair colour
      sex_ratio.py          natural sex ratio at birth (105:100)
      data/diseases.json    disease panel + regional evidence (DRAFT until validated)
      data/references.json  every source, with link-check status
    ai/                     AI explanation engine (Step B), isolated from genetics/
    i18n.py                 server-side AR/EN/DE text for every engine key
    api.py                  /api routes
    auth.py                 roles (admin/member) stored in MongoDB
  tests/                    pytest: unit + integrity + API integration
frontend/src/
  pages/, components/genova/, i18n/, lib/api.js
docs/                       audit, migration plan, disease panel, architecture, science
scripts/clerk_test_session.py   dev-only test session helper
```

## Run tests
```
cd backend && python -m pytest tests -n 0
```

## Environment variables
See `backend/.env.example` and `frontend/.env.example`. Clerk keys are set by the platform in `backend/.env`.
The frontend holds no secrets. `.env` files are git-ignored.

## Docs
- `docs/REPOSITORY_REVIEW_AND_MIGRATION_PLAN.md`: audit of the 5 legacy repos + migration plan
- `docs/DISEASE_PANEL_PROPOSAL.md`: 10-condition panel, sources, validation process
- `docs/ARCHITECTURE.md`: separation, API, security
- `docs/SCIENCE.md`: methods, certainty tiers, simplifications

Legacy repositories (`aliboozahmad-glitch/baby-gender-*`) were reviewed read-only and never modified.
