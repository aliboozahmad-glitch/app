# GENOVA AI — Repository Review & Migration Plan

Status: AWAITING YOUR APPROVAL. No existing code has been modified, replaced or deleted.
Decisions received: real-biology sex info · baby-face as premium AI artwork · AR/EN/DE · subscribers-only access · user picks region.
Reviewed: June 2026 (read-only clones of all 5 repositories).

---

## 1. Repositories reviewed

| Repo | Last commit | Contents | Verdict |
|---|---|---|---|
| `baby-gender-app` | 2025-11-16 "Remove MongoDB dependency" | Expo (React Native) app, 4 screens (home, gender, genetic, traits) + FastAPI backend v1 + guides (APK build, GitHub upload, DB access) | Superseded by `baby-gender-backend` (backend) and `predict-v2` (frontend). Keep for history. |
| `baby-gender-backend` | 2025-12-21 "Change startCommand port" | Standalone FastAPI backend (Railway/Docker): gender, genetic diseases, traits, baby-face (Replicate), history/export/statistics | Most recent backend. Logic must be rebuilt (see §3). |
| `baby-gender-predict-v2` | 2025-11-17 "Complete Traits section with scientific calculator and sources" | Expo app v2: Home, Gender, Genetic Diseases list + detail (with CDC/MOH sources), Traits + Results + Sources, `GeneticCalculator.js` | Best content (sources, Mendelian carrier text, height formula). Preserve content, re-verify numbers. |
| `baby-gender-privacy` | 2025-11-21 "Translate privacy policy to German" | Static privacy policy (AR / EN / DE) | Preserve; rewrite for GENOVA (accounts, payments, AI processing, health-data). |
| `baby-gender-privacy-2` | — | Empty repository (0 commits) | Nothing to migrate. |

---

## 2. Feature inventory

| # | Feature | Where | Duplicated? | Scientific status | Plan |
|---|---|---|---|---|---|
| F1 | Baby gender prediction from family birth-order patterns (lookup table, "52 cases") | `gender_prediction_logic.py` in app + backend | Yes (2 copies, backend has extra cases 53–80) | **Not scientifically supported.** A baby's sex is set by the father's sperm (X or Y), about 51% male / 49% female at birth. Relatives' birth order has no proven predictive value. | **Decision needed (Q1)** |
| F2 | Gender "confidence %" | same | Yes | **Generated with `random.randint` (70–90, 50–60, 40–50)**; 3rd+ child uses `random.choice`. This breaks requirement #5. | Remove random numbers completely. |
| F3 | Genetic disease risk (thalassemia, sickle cell, hemophilia, color blindness, CF, Duchenne) | `server.py` `/predict-genetic-diseases` | Yes (v1 also used baby gender) | **Unreliable**: risk % is hard-coded 25/55/75 based on *how many diseases were typed*, not genetics. Matches on keyword substrings. | Rebuild as carrier-status Mendelian calculator (AR / X-linked / AD) with cited carrier frequencies. |
| F4 | Disease detail pages with "25% affected / 50% carrier / 25% healthy" | `predict-v2/DiseaseDetailScreen.js` | No | **Correct** for autosomal recessive carriers. X-linked text correct for carrier mother × unaffected father; "higher risk" phrasing vague. | Preserve text; replace with computed results from the engine. |
| F5 | Down syndrome by maternal age (1/1500 <35, 1/100 >40) | `predict-v2` | No | Chromosomal, **not inherited by Mendelian rules**. Figures roughly match published age-risk tables but are rounded and the "<35 = 1/1500" is inaccurate across ages 20–34. | Move to "population statistics" (estimate tier) with a cited age table (e.g. ACOG / Morris et al. 2002). |
| F6 | Eye color % table (e.g. Brown×Brown 75/18/6/1, Blue×Blue 99/1) | `GeneticCalculator.js` | No | **Uncertain / folk tables** labelled "NIH" but not traceable to an NIH publication. Eye colour is polygenic (HERC2/OCA2 + others). | Re-implement as clearly-labelled **estimate** with honest wording and published model reference (e.g. HIrisPlex), no fake precision. |
| F7 | Hair color % table | `GeneticCalculator.js` | No | Same — labelled "Edinburgh", not verifiable. Black hair input not well modelled. | Estimate tier, qualitative only, cited. |
| F8 | Skin tone % table | `GeneticCalculator.js` | No | Polygenic, not predictable with these numbers. | Estimate tier, qualitative only (range between parents). |
| F9 | Height: mid-parental formula ((M+F±13)/2, ±8 cm) | `GeneticCalculator.js` | No | **Valid, established** (Tanner mid-parental height; ±8.5 cm ≈ 2 SD). Defaults of 165/175 cm silently used when input missing — bad. | Preserve; require input, cite Tanner 1970. |
| F10 | Backend traits endpoint (dominance score averaging, "percentages") | `server.py` `/predict-traits` | Conflicts with F6–F9 | **Invalid**: averages arbitrary scores; % is meaningless. | Replace with F6–F9 engine. |
| F11 | AI explanation (OpenAI gpt-4o-mini) | `server.py` | Yes | Explanation was generated but **hidden from users** and stored as "proprietary". | Rebuild as separate AI explanation engine (Claude Opus 5.5) that only explains engine results, never invents numbers. |
| F12 | Baby face generation from parent photos (Replicate "baby-mystic") | `baby-gender-backend` | No | Entertainment image, not a genetic prediction. Photos sent as base64. | **Decision needed (Q2)** |
| F13 | Prediction history / export-all-data / statistics | `server.py` | Yes | **Security issue**: no auth — anyone could export every user's data. | Rebuild: per-user history behind login; admin-only stats. |
| F14 | Bilingual UI Arabic/English (+ German explanation function, German privacy policy) | all | — | n/a | Preserve AR/EN/DE (**Q3**). |
| F15 | Trusted source links (CDC, MOH Saudi, MedlinePlus, NHGRI, Mayo Clinic Arabic) | `predict-v2` | — | Good. Some CDC URLs have moved. | Preserve, verify each link, attach to every result. |
| F16 | Mobile build docs (EAS/APK), Railway/Render/Docker deploy | all | Yes | n/a | Archive; new deploy docs for GENOVA. |
| F17 | Privacy policy AR/EN/DE | `baby-gender-privacy` | — | n/a | Rewrite for new data processing. |

---

## 3. Problems found (must fix in GENOVA)

### Scientific
1. `random.randint` / `random.choice` used to produce "confidence" and even the predicted sex for 3rd+ children.
2. Gender pattern table: wife and husband lists are concatenated into one key, so "2 + 2 children" and "1 + 3 children" (or "3 + 1") produce the same key. 10 keys are defined twice (72 entries → only 62 unique), and the table cannot tell which family had which child. Any pattern not in the table defaults to "male".
3. Disease risk % depends on number of typed diseases, not on inheritance.
4. Trait "percentages" are arithmetic on made-up dominance scores.
5. Source labels ("NIH", "Edinburgh") attached to numbers that cannot be traced to those sources.
6. Height uses silent default parent heights.

### Security
1. **An Emergent LLM key is committed in plain text** in `baby-gender-app/DOWNLOAD_APP_GUIDE.md` (line 234). It should be treated as leaked — rotate it and remove it from git history.
2. `.env` committed in `baby-gender-predict-v2`.
3. `/api/export-all-data`, `/api/history`, `/api/statistics` have no authentication.
4. CORS `allow_origins=["*"]` with credentials.
5. `HTTPException(detail=str(e))` leaks internal errors.
6. No input validation (free-text genders, unlimited base64 image size).
7. No tests (`tests/__init__.py` empty; `backend_test.py` only smoke-tests endpoints).

### Engineering
- Two diverging backend copies; business logic inside route handlers; deprecated `datetime.utcnow()`; MongoDB removed so history never worked in production.

---

## 4. Proposed GENOVA AI architecture

```
genova-ai/
├── backend/                       FastAPI
│   ├── app/
│   │   ├── main.py                app factory, CORS allow-list, error handlers
│   │   ├── core/                  config (env only), security (JWT, bcrypt), rate limit
│   │   ├── genetics/              PURE calculation engine (no I/O, no AI, no randomness)
│   │   │   ├── mendelian.py       Punnett squares: AD, AR, X-linked dom/rec, codominant
│   │   │   ├── blood_type.py      ABO + Rh exact outcomes from genotype/phenotype
│   │   │   ├── carrier_risk.py    disease carrier risk (Bayes w/ cited carrier frequencies)
│   │   │   ├── polygenic.py       eye/hair/skin estimates, height mid-parental (Tanner)
│   │   │   ├── sex_ratio.py       biological sex probability (≈51/49, cited) — replaces F1/F2
│   │   │   └── data/              versioned JSON: diseases, frequencies, references
│   │   ├── ai/explain/            explanation engine (Claude Opus 5.5) — receives engine
│   │   │                          output, explains it, cannot change numbers
│   │   ├── ai/artwork/            baby-face ARTWORK generator (premium, separate module,
│   │   │                          never imports genetics/, output watermarked 'AI artwork')
│   │   ├── api/v1/                routers: auth, analyses, explain, billing, history, admin
│   │   ├── models/                Pydantic schemas + Mongo documents
│   │   └── services/              subscription/entitlement checks, history persistence
│   └── tests/                     pytest: every probability table verified (sums = 1,
│                                  known textbook crosses), API + auth + billing tests
├── frontend/                      React web app (AR / EN / DE, RTL support)
├── docs/                          ARCHITECTURE.md, SCIENCE.md (methods + references),
│                                  API.md, SECURITY.md, MIGRATION.md, PRIVACY.md
└── .github/                       CI (lint + tests), PR template, .gitignore, no secrets
```

## 4a. Two kinds of input — never mixed

| Input source | Example | Result label | How it's computed |
|---|---|---|---|
| **Individual genetic test result** (user states a confirmed genotype/carrier status from a lab report) | "Mother: confirmed HbS carrier (AS)" | `certainty: "established"` | Exact Mendelian Punnett square. Results like 1/4, 1/2 are mathematically exact *given the stated genotypes*. |
| **Unknown status → population carrier frequency** (user picks a region) | "Father: not tested, region: Gulf" | `certainty: "population_estimate"` | Bayesian: P(carrier) taken from a cited regional frequency, combined with Mendelian rules. Shown as an estimate with its source and range. |
| **Family history only** | "Father's brother has CF" | `certainty: "population_estimate"` | Standard prior-risk rules (e.g. unaffected sibling of affected person = 2/3 carrier), cited. |
| **Polygenic traits** (eye, hair, skin) | "Both parents brown eyes" | `certainty: "uncertain_estimate"` | Qualitative likelihood bands only, no false precision. |
| **Height** | parents' heights in cm | `certainty: "statistical_estimate"` | Tanner mid-parental height ±8.5 cm (≈2 SD). |
| **Biological sex** | none needed | `certainty: "population_statistic"` | ~51.2% male at birth (WHO sex-ratio data). Family patterns are NOT used. |

The UI shows a different badge and colour for each tier, and the AI explanation is told which tier it is explaining.

## 4b. Standard result format (every endpoint)

```json
{
  "analysis_type": "carrier_risk",
  "certainty": "established | population_estimate | statistical_estimate | uncertain_estimate | population_statistic",
  "method": "Mendelian Punnett square (autosomal recessive)",
  "inputs_used": {"mother": "carrier (tested)", "father": "unknown, region=gulf"},
  "outcomes": [{"label": "affected", "probability": 0.0125, "fraction": "1/80", "range": [0.005, 0.03]}],
  "assumptions": ["Complete penetrance", "No consanguinity"],
  "references": [{"id": "who-hb-2008", "title": "...", "url": "...", "accessed": "2026-06"}],
  "engine_version": "genova-genetics 1.0.0",
  "data_version": "frequencies 2026-06",
  "disclaimer": "Educational information, not a medical diagnosis. Consult a genetic counsellor."
}
```
Same inputs + same data version → identical output, always (no randomness anywhere; enforced by a test that greps the engine for `random`).

## 4c. Access & subscription (your decision: subscribers only)

- Public without login: landing page, pricing, sources/methods page, privacy policy, terms.
- Everything else requires **login + active subscription**, checked on the **server** for every API call (not just hidden in the UI).
- Email + password login (bcrypt hashing, JWT in httpOnly cookie, brute-force lockout, admin account).
- Stripe Checkout for subscriptions; subscription status updated by Stripe webhook (signature verified), never trusted from the browser.
- Baby-face artwork: premium feature, extra per-day limit to control image costs, parent photos stored privately and deletable by the user.
- Rate limiting per user, CORS allow-list, generic error messages, all keys only in server `.env`.
- Admin: user list, subscription status, aggregate usage stats (no personal genetic data export).

## 4d. Languages
Arabic (RTL), English, German for UI, results, disclaimers and AI explanations. Scientific references stay in their original language.

---

## 5. Migration plan (phased, nothing deleted)

| Phase | Work | Old repos touched? |
|---|---|---|
| 0 | ✅ This audit. Old repos remain untouched (read-only reference). | No |
| 1 | Science foundation: genetics engine, disease + regional frequency data with references, full unit tests. | No |
| 2 | API: auth, analyses endpoints, validation, error handling, saved history. | No |
| 3 | AI explanation engine (Claude Opus 5.5) with guardrails: can only explain numbers it receives. | No |
| 4 | Web app (AR/EN/DE), result cards with certainty badges and sources. | No |
| 5 | Stripe subscriptions, server-side access control, admin panel. | No |
| 6 | Baby-face AI artwork (premium, clearly labelled, separate module). | No |
| 7 | Docs (ARCHITECTURE, SCIENCE, API, SECURITY, PRIVACY in AR/EN/DE), CI, GitHub-ready. | No |
| 8 | Later, only with your approval: rotate the leaked key, point the old mobile apps at the GENOVA API or retire them. | Only with approval |

### Old feature → GENOVA mapping
| Old | GENOVA |
|---|---|
| F1/F2 gender predictor | `sex_ratio.py` — real biology (~51/49), explains X/Y. The old table isn't used. |
| F3 disease risk | `carrier_risk.py` — tested genotype OR regional frequency |
| F4 disease detail pages + sources | Disease library pages, computed results, verified links |
| F5 Down syndrome | Maternal-age population statistic, cited age table |
| F6–F8, F10 eye/hair/skin | `polygenic.py`, uncertain-estimate tier |
| F9 height | `polygenic.py` mid-parental height (Tanner) |
| F11 AI explanation | `ai/explain/` (Claude Opus 5.5), visible to subscribers |
| F12 baby face | `ai/artwork/` premium artwork, never a prediction |
| F13 history/export/stats | Per-user history + admin stats (secured) |
| F14 AR/EN/DE | Full i18n with RTL |
| F15 sources | `references.json`, linked from every result |
| F16 build/deploy docs | New docs (old ones archived in old repos) |
| F17 privacy policy | Rewritten for accounts, payments, AI, health data (AR/EN/DE) |

---

## 6. Missing features (new in GENOVA, not in any old repo)

1. Single-gene Punnett calculator for any trait: autosomal dominant / recessive, X-linked dominant / recessive, codominant / incomplete dominance.
2. ABO + Rh blood-type prediction (exact Mendelian outcomes, from phenotype or known genotype).
3. Regional carrier-frequency selector (Gulf / Middle East, Europe, Africa, South Asia, East Asia, Americas, global).
4. Distinction between tested genotypes and population estimates.
5. User accounts, saved analysis history, admin panel.
6. Paid subscriptions with server-side enforcement.
7. Certainty badges + assumptions + references on every result.
8. Automated tests (none existed) + CI.
9. Proper input validation and error handling.
10. Shareable/printable result report (optional, can be later).

## 7. Still needed from you (can be decided during build)

- **Subscription price and billing period** (e.g. monthly / yearly; currency). Default if not given: one monthly plan in USD (placeholder price, easy to change).
- **Old mobile apps**: keep them live on the old backend for now, or move later? Default: untouched.
- **Leaked key**: the Emergent LLM key in `baby-gender-app/DOWNLOAD_APP_GUIDE.md` should be rotated. I won't touch the old repo; you can rotate it from your Emergent profile.
- Disease list for v1. Default: thalassemia (β), sickle cell, G6PD deficiency (X-linked, important for the Gulf), cystic fibrosis, hemophilia A/B, Duchenne, red-green color blindness, PKU, SMA, Tay-Sachs. All figures will be taken from published sources and cited, not invented.

---

## 8. Scientific honesty rules (built into code + tests)

- No `random` anywhere in the genetics engine (test-enforced).
- Every number traces to a formula or a cited data entry; data entries without a reference fail the test suite.
- The AI never produces probabilities; it receives the engine result and explains it, and the response is checked for unexpected percentages.
- No claims of diagnostic accuracy. Every result shows "educational, not a diagnosis".
