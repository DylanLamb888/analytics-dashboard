# Order Analytics Dashboard – Prototype Design Brief

## 1. Project Overview

Build a **sleek, web‑based analytics dashboard** that ingests order data (CSV), normalises & geo‑enriches it, and presents interactive visual insights (top‑selling items, regional sales, temporal trends) with export capability. Prototype will run on dummy data but meet production‑quality standards in code structure, test coverage, and CI/CD.

## 2. Objectives

1. Deliver a fully working prototype within 1 sprint (≤ 5 days).
2. Match the visual/interaction quality of modern SaaS dashboards (Think Stripe or Linear).
3. Lay groundwork for scaling to real client data with minimal refactor.

## 3. Success Criteria

| Metric                                                              | Target |
| ------------------------------------------------------------------- | ------ |
| End‑to‑end demo runs in < 3 s on 1k dummy orders                    | ✅      |
| 100% pass on unit+integration test suite (≥ 95% coverage)           | ✅      |
| Lighthouse performance + accessibility ≥ 90                         | ✅      |
| CI pipeline finishes < 5 min (build, lint, test, deploy to staging) | ✅      |

## 4. Assumptions & Constraints

* **US‑only** addresses for MVP.
* Prototype hosted on free tiers (Streamlit Community Cloud + Fly.io/Railway) – must stay within 512 MB RAM.
* CSV ≤ 5 MB; production path will stream larger files to S3 > Postgres.

## 5. Data Model & Dummy Set

### 5.1 Core Schema (orders.csv)

| Field            | Type          | Example                         |
| ---------------- | ------------- | ------------------------------- |
| order\_id        | string(uuid4) | `7b1d6…`                        |
| order\_date      | ISO‑8601      | `2025-02-14T13:07:02Z`          |
| customer\_name   | string        | `Jamie Lee`                     |
| address\_line    | string        | `123 Maple St, Denver CO 80218` |
| item\_sku        | string        | `SKU‑A12‑BLK`                   |
| item\_name       | string        | `Transit Backpack`              |
| quantity         | int           | 2                               |
| unit\_price\_usd | decimal(10,2) | 79.00                           |

### 5.2 Dummy Data Generation

* Use Faker + factory‑boy to create **1 000 rows** covering 8 SKUs, 200 unique customers, 50 ZIPs across 10 states, spread over the last 180 days.
* Script committed under `/scripts/generate_dummy_data.py`; executed in CI to ensure repeatable sample.

## 6. System Architecture

```
┌─────────────────┐        ┌────────────────┐
│ Next.js Frontend│<──────>│ FastAPI backend│
│  (iframe shell) │        │ + DuckDB (in‑mem) │
└────────┬────────┘        └────────┬───────┘
         │ iframe stream            │
         ▼                         ▼
   ┌──────────────┐        ┌─────────────────┐
   │ Streamlit App│<──────>│ ZIP Geo JSON &  │
   │  (Plotly)    │        │  persisted CSV  │
   └──────────────┘        └─────────────────┘
```

* **FastAPI** exposes `/upload`, `/orders`, `/report` endpoints.
* **DuckDB** persists during container life; upgrade path → Postgres + PostGIS.
* **Streamlit** consumes `/orders` with reactive caching.
* **Next.js** uses Tailwind + Framer Motion for branded chrome, auth gating, deep links.

## 7. Technology Stack

| Layer     | Tech                                                                      | Rationale                                      |
| --------- | ------------------------------------------------------------------------- | ---------------------------------------------- |
| Front‑end | Next.js 14 · React 19 · Tailwind 3 · Framer Motion                        | Consistent with existing engineering workflow. |
| API       | FastAPI 0.111 · Pydantic 2                                                | Automatic OpenAPI, async speed, strong typing. |
| Data      | Pandas 2 + DuckDB 1.5                                                     | Zero external DB, SQL queries.                 |
| Geo       | `usaddress`, `uszipcode`, pre‑baked ZIP GeoJSON                           | Rapid, accurate US parsing.                    |
| Viz       | Streamlit 1.35 + Plotly Express 5                                         | Fast prototyping, no custom webpack.           |
| DevOps    | Docker, GitHub Actions, Fly.io (staging), Streamlit Community Cloud (viz) |                                                |
| Testing   | Pytest, React Testing Library, Pydantic validation tests                  |                                                |
| Quality   | ruff, mypy, TypeScript strict, Prettier                                   |                                                |

## 8. Functional Requirements

1. **CSV Upload** – Drag‑and‑drop widget. Accepts `.csv` ≤ 5 MB. Reject others; show error.
2. **Normalization Pipeline**

   * Strip whitespace, fix encoding.
   * Parse address → street, city, state, ZIP, lat, lon.
   * Compute `order_total` (`quantity×unit_price`), `order_day`.
3. **Interactive Dashboard**

   * Date range picker (Last 30/90/Custom).
   * Top‑N items bar chart (toggle by quantity or revenue).
   * Time‑series revenue line chart (daily granularity; range‑slider zoom).
   * Choropleth map by ZIP (revenue heat‑map).
4. **Drill‑Down** – Row‑level data table (streamlit‑aggrid) with search & column filters.
5. **Export** – Download current view as XLSX; hotlink to `/report?filters…`.
6. **Auth Stub** – Placeholder JWT flow; protected routes; extendable.

## 9. Non‑Functional Requirements

* **Performance** –  p95 < 200 ms API latency, < 150 ms first chart render (1 k rows).
* **Reliability** –  Graceful 4xx/5xx JSON errors; typed error envelopes.
* **Security** –  OWASP top‑10 baseline: helmet headers, CORS whitelist, rate limiting (slowapi), no secrets in repo.
* **Accessibility** –  WCAG 2.1 AA: proper alt text, colour contrast ≥ 4.5:1.
* **Observability** –  Structured logs (loguru), Prometheus metrics endpoint.

## 10. UI / UX Guidelines

* Minimalist dark‑on‑light theme; accent brand colour.
* Responsive breakpoints: mobile → stacked, desktop ≥ 1024 px → 2‑column grid.
* Micro‑interactions: fade‑in charts, hover tooltips, skeleton loaders on async.

## 11. Testing & QA

| Layer     | Tests                                                                     |
| --------- | ------------------------------------------------------------------------- |
| ETL       | Pandas transform unit tests (edge cases: malformed address, missing ZIP). |
| API       | Pytest + httpx integration (200, 400, 413 cases).                         |
| Front‑end | Jest + RTL: component props, date filter behaviour, export button state.  |
| E2E       | Playwright: upload → dashboard → export.                                  |

## 12. DevOps & Deployment

* **Docker** multi‑stage: lint/test → distroless runtime.
* **GitHub Actions** pipeline: lint → typecheck → unit tests → build → deploy to staging.
* **IaC**: fly.toml + streamlit‑cloud‑app.toml.

## 13. Deliverables

1. Repo with clean commit history and README.
2. Live URLs: staging API + dashboard.
3. Loom demo (≤ 3 min) walking through main flows.
4. PDF hand‑off containing architecture & next‑step roadmap.

## 14. Timeline (T‑0 = kickoff)

| Day | Milestone                            |
| --- | ------------------------------------ |
| T‑0 | Project setup, dummy data script.    |
| T‑1 | ETL pipeline + tests.                |
| T‑2 | Dashboard MVP (charts + filters).    |
| T‑3 | Export + polishing, Lighthouse pass. |
| T‑4 | QA, deployment, Loom recording.      |

## 15. Risks & Mitigations

* **Address parse failures** – fallback to ZIP only; log unknown cases.
* **Streamlit resource limits** – aggressively cache & prune; scale to dedicated VM if hit.
* **CSV variance** – implement schema validation with clear error UI.

## 16. Next Steps

1. Confirm brief & timelines with client.
2. Approve visual style mock.
3. Begin sprint T‑0.
