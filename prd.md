# Order Analytics Dashboard — Product Requirements Document (PRD)

## 1. Purpose

Deliver a production‑grade, web‑based analytics dashboard that converts raw order data into actionable insights for business stakeholders. The prototype will use dummy data yet conform to enterprise‑level code quality, scalability, and UX standards so it can be taken to production with minimal re‑work.

## 2. Background & Problem Statement

Growth‑stage e‑commerce merchants lack an out‑of‑the‑box tool that correlates orders, geography, and product mix in realtime. Existing BI stacks (e.g., Looker, Tableau) are heavy, expensive, and slow to customise. The client needs a lightweight, embeddable dashboard that surfaces key sales signals (top items, regional hotspots, time‑based trends) and enables rapid drill‑down without specialised BI skills.

## 3. Goals & Success Metrics

| Goal                | KPI                                 | Target            |
| ------------------- | ----------------------------------- | ----------------- |
| Actionable insights | Time to first chart render          | ≤ 2 s on 1 k rows |
| Sales visibility    | Coverage of required visualisations | 100 %             |
| Reliability         | System uptime during demo period    | 99.5 %            |
| Code quality        | Automated test coverage             | ≥ 95 %            |
| Accessibility       | Lighthouse a11y score               | ≥ 90              |

## 4. User Personas

| Persona            | Needs                               | Pain Points                  |
| ------------------ | ----------------------------------- | ---------------------------- |
| **Owner/GM**       | Snapshot of revenue drivers         | Spends hours in spreadsheets |
| **Ops Analyst**    | Filter by date, export data         | Manual VLOOKUP hell          |
| **Marketing Lead** | Identify geo clusters for campaigns | Can’t tie ZIP codes to sales |

## 5. Scope

### 5.1 In‑Scope Features

1. **CSV Upload & Validation** (≤ 5 MB)
2. **ETL Pipeline**: normalise, parse address, enrich ZIP → lat/lon
3. **Dashboard UI**

   * Date range picker (Last 30/90/Custom)
   * Charts: Top‑N items, Revenue over time, Choropleth by ZIP
   * Paginated data table with search & column filters
4. **Exports**: current view → XLSX
5. **Auth Stub**: email+PW, JWT, role=admin|viewer
6. **Observability**: structured logs, Prometheus metrics
7. **Performance Budget**: p95 API < 200 ms
8. **CI/CD**: lint, test, build, deploy to staging (Fly.io + Streamlit Cloud)

### 5.2 Out‑of‑Scope (MVP)

* Multi‑currency support
* Non‑US addresses
* Real‑time Kafka ingestion
* Advanced cohort analysis & predictive metrics

## 6. Detailed Functional Requirements

### 6.1 CSV Upload

* **FR‑1.1** Accept `.csv` via drag‑and‑drop or file picker.
* **FR‑1.2** Reject files > 5 MB or non‑CSV; surface error toast.
* **FR‑1.3** Persist original file hash for audit.

### 6.2 Data Processing

* **FR‑2.1** Trim whitespace, coerce datatypes, dedupe `order_id`.
* **FR‑2.2** Address parsing: split into street, city, state, ZIP using `usaddress`.
* **FR‑2.3** Geo‑enrich lat/lon via cached ZIP lookup (uszipcode), max 10 ms/row.
* **FR‑2.4** Compute derived fields: `order_total`, `order_day`, `weekday`.

### 6.3 API

* **FR‑3.1** `POST /upload` returns JSON `{rows, errors}`.
* **FR‑3.2** `GET /orders?start=…&end=…` returns filtered dataset.
* **FR‑3.3** `GET /report.xlsx?filters…` streams file.
* **FR‑3.4** All endpoints secured via Bearer token header.

### 6.4 Dashboard UI

* **FR‑4.1** Show skeleton loaders while fetching.
* **FR‑4.2** Charts update in < 300 ms after filter change.
* **FR‑4.3** Map uses ZIP GeoJSON; hover tooltip shows revenue, order count.
* **FR‑4.4** Table allows column hide/show and CSV export (client‑side).

### 6.5 Exports

* **FR‑5.1** Use Pandas `to_excel` with styled header row.
* **FR‑5.2** File downloads via signed URL expiring in 60 min.

### 6.6 Authentication & RBAC

* **FR‑6.1** Roles: `admin` (upload, delete data) vs `viewer` (view/export only).
* **FR‑6.2** Session valid 7 days; refresh token flow.

### 6.7 Accessibility & i18n

* **FR‑7.1** Keyboard navigable, accessible labels, ARIA tags.
* **FR‑7.2** All text behind i18n keys; only `en‑US` shipped in prototype.

### 6.8 Observability

* **FR‑8.1** Log trace‑id per request; expose `/metrics`.
* **FR‑8.2** Error alerting via Slack webhook on staging.

## 7. Non‑Functional Requirements

| Category        | Requirement                                              |
| --------------- | -------------------------------------------------------- |
| Performance     | p95 API < 200 ms; JS bundle < 200 KB gzip.               |
| Scalability     | Handle 50 k rows with linear degradation < 1.5×.         |
| Security        | OWASP top‑10 mitigations; rate‑limit 100 req/min per IP. |
| Maintainability | Code climate score ≥ A; 100 % typed Python & TS.         |
| Reliability     | Auto‑restart on failure; graceful shutdown w/ SIGTERM.   |
| Accessibility   | WCAG 2.1 AA compliance.                                  |

## 8. Technical Architecture (High‑Level)

* **Frontend**: Next.js 14 SSR → iframe to Streamlit (Plotly)
* **Backend**: FastAPI + Pydantic → DuckDB in‑mem
* **CI/CD**: GitHub Actions → Fly.io (API) + Streamlit Cloud (viz)
* **Testing**: Pytest + httpx; Playwright E2E; Jest (React)

## 9. Dependencies & Integrations

* `usaddress`, `uszipcode` (USPS DB)
* Pre‑baked ZIP GeoJSON (TIGER/Line 2023)
* Docker, GitHub Actions, Fly.io, Streamlit Cloud accounts

## 10. Risks & Mitigations

| Risk                     | Impact             | Likelihood | Mitigation                                              |
| ------------------------ | ------------------ | ---------- | ------------------------------------------------------- |
| Streamlit free tier OOM  | Demo outage        | Medium     | Aggressive caching, slim charts; fallback to local run. |
| Address parse edge cases | Incorrect geo data | Low        | Log & default to city/state; alert threshold > 1 %.     |
| Large CSV upload         | API timeout        | Low        | Enforce 5 MB limit; display friendly error.             |

## 11. Timeline & Milestones

| Date  | Milestone                                            |
| ----- | ---------------------------------------------------- |
| Day 0 | Kickoff; repo/CI setup; freeze dummy schema.         |
| Day 1 | CSV upload + ETL pipeline complete; unit tests pass. |
| Day 2 | Core API & auth stub; staging deploy.                |
| Day 3 | Dashboard UI + filters & charts; Playwright E2E.     |
| Day 4 | Export, polish, Lighthouse 90+.                      |
| Day 5 | User acceptance; Loom recording.                     |

## 12. Acceptance Criteria

* All **In‑Scope Features** implemented & passing tests.
* Demo script runs without manual intervention.
* No critical or high‑severity bugs open.
* KPIs in §3 met or exceeded.

## 13. Analytics & Instrumentation

* Pageview + click tracking via PostHog (self‑host on Fly.io).
* Custom events: file upload, filter apply, export click.

## 14. Open Questions

1. Will production require multi‑currency support? (Y/N)
2. Preferred auth provider (Auth0, Clerk, custom)?
3. SLA expectations for production? (99.9 %?)

## 15. Future Enhancements

* Real‑time ingestion via Kafka + Materialize.
* Cohort analysis (first‑to‑repeat, retention curves).
* AI‑powered anomaly detection (spikes, dips).
