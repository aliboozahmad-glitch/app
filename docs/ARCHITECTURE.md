# Architecture, API & security (Step A)

## Separation
`genova/genetics` (pure, deterministic) → `genova/i18n` (text) → `genova/api` (HTTP, auth, storage).
`genova/ai` is a separate package. It may read finished results and must never import the calculators or create numbers.

## API (all under /api)
| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /health | public | status + engine version |
| GET | /catalog?lang= | public | modes, regions, disease panel |
| GET | /references | public | all sources |
| GET | /me | user | id, role |
| POST | /analyses/{mendelian, blood-type, carrier-risk, height, pigmentation, sex-ratio}?lang= | user | run + save |
| GET | /analyses?lang= | user | own history |
| GET / DELETE | /analyses/{id} | user (owner only, others get 404) | view / delete |
| GET | /users | admin | user list |
| PATCH | /users/{id}/role | admin | change role (keeps ≥1 admin) |

Errors: 400 `{detail:{code,message}}` for engine input errors (localised), 422 `{detail:{code:"validation_error",errors}}`, 401/403/404/429, 500 with a generic message only.

## Security
- Clerk session JWT verified on the server for every protected call; roles are read from MongoDB, never from the client.
- Strict request schemas (`extra="forbid"`), length limits, enumerated values.
- Per-user rate limit: 30 analyses/minute (in-memory; move to Redis when scaling to several workers).
- Data is scoped to the owner inside each query.
- No secrets in the frontend or the repo. Clerk keys live only in `backend/.env`.
- Headers: `X-Content-Type-Options: nosniff`, `Referrer-Policy`.
- Planned for Step C: subscription gating on all calculators, Stripe webhooks, admin pricing.
