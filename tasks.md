# InsideX — Build Plan & Task List

**Goal:** Ship a usable web app that surfaces insider-trading signals from SEC Form 4 data, with a clean API, a first ML model, and a polished UI.

**Stacks**

* **Backend**: FastAPI, SQLAlchemy/SQLite (existing DB), Pydantic, Uvicorn
* **Worker**: Python (scheduled scraper `scrape.py`, incremental updates), APScheduler/cron
* **ML**: scikit-learn (baseline), xgboost (optional), joblib for model artifacts
* **Frontend**: Next.js (App Router), React, TailwindCSS, TanStack Query, Chart.js (or Recharts)
* **DX/Infra**: Docker, Ruff/Black, Pytest, GitHub Actions

---

## Milestones

1. **M1 — API & Data Access (Backend)**

* Read-only endpoints over existing DB
* Pagination, filtering, sane response times

2. **M2 — Baseline ML Signal**

* Deterministic feature pipeline + train/eval + saved artifact
* `/signals` endpoint returning ranked tickers & rationale

3. **M3 — Frontend MVP**

* Landing, Dashboard, Ticker page, Insider page
* Sorting/filtering, charts, and fast search



---

## Project Setup

* **Folders**

  ```
  backend/
    app/
      __init__.py
      main.py
      api/
        __init__.py
        routes_trades.py
        routes_companies.py
        routes_insiders.py
        routes_signals.py
      core/
        config.py
        deps.py
      models/            # Pydantic schemas
        __init__.py
        trade.py
        company.py
        insider.py
        signal.py
      services/
        __init__.py
        trade_service.py
        signal_service.py
        feature_store.py
      ml/
        __init__.py
        train.py
        evaluate.py
        features.py
        artifacts/
          model.joblib
          features.yaml
    database.py          # existing
    analyze.py           # existing
    scrape.py            # existing
    requirements.txt
    Dockerfile
    pyproject.toml (optional)

  frontend/
    app/
      layout.tsx
      page.tsx           # Landing
      dashboard/page.tsx
      ticker/[symbol]/page.tsx
      insider/[name]/page.tsx
    components/
      Nav.tsx
      Cards.tsx
      TradeTable.tsx
      SignalBadge.tsx
      Charts.tsx
      Filters.tsx
    lib/
      api.ts
      types.ts
    public/
    package.json
    tailwind.config.js
    tsconfig.json
  ```

---

## Tasks (checklist)

### [Backend] M1 — Public API over existing DB

* [ ] **B-1 | Boot FastAPI app**

  * **Files**: `backend/app/main.py`, `backend/app/core/config.py`
  * **Do**: Init FastAPI, CORS, healthcheck `/healthz`.
  * **Accept**: `uvicorn app.main:app` returns 200 at `/healthz`.

* [ ] **B-2 | Pydantic schemas**

  * **Files**: `backend/app/models/{trade,company,insider}.py`
  * **Do**: Define response models mirroring DB fields (safe subset).
  * **Accept**: Schemas validate example payloads; mypy passes.

* [ ] **B-3 | Trade Service & Pagination**

  * **Files**: `backend/app/services/trade_service.py`
  * **Do**: DB read functions (limit/offset, filters, sort by `filing_date`).
  * **Accept**: Query returns within <300ms on sample DB; supports:

    * filters: `ticker`, `insider_name`, `trade_type` (Buy/Sell), `flag` (e.g., “10% Owner”), `date_from/date_to`, `min_value_usd`.

* [ ] **B-4 | Routes: /trades, /companies, /insiders**

  * **Files**: `backend/app/api/routes_{trades,companies,insiders}.py`
  * **Do**:

    * `GET /trades`: filters + pagination
    * `GET /companies/{ticker}`: summary stats (buys/sells, recent moves)
    * `GET /insiders/{id or name}`: profile + last N trades
  * **Accept**: OpenAPI docs show routes; curl works with filters.

* [ ] **B-5 | Company & Insider summaries**

  * **Files**: `backend/app/services/trade_service.py`
  * **Do**: Helper aggregations (last 90d buy/sell count, net $).
  * **Accept**: `GET /companies/AAPL` returns computed aggregates.

* [ ] **B-6 | Error handling & validation**

  * **Files**: `backend/app/core/deps.py`, route files
  * **Do**: 422 on invalid params, clear error payloads.
  * **Accept**: Negative `limit` rejected; bad dates error.

---

### [ML] M2 — Baseline Model & Signals

* [ ] **ML-1 | Feature Spec**

  * **Files**: `backend/app/ml/features.py`, `backend/app/ml/features.yaml`
  * **Do**: Define features (per filing & rolled-up):

    * Filing: `delta_shares`, `dollar_value`, `price_vs_30dma`, `role_onehot` (CEO/VP/10% owner), `own_pct_after`, `cluster_rank` (insider’s historical hit-rate), `company_buy_ratio_90d`, `time_to_report_days`.
  * **Accept**: `features.yaml` lists each feature with type & source.

* [ ] **ML-2 | Labeling**

  * **Files**: `backend/app/ml/train.py`
  * **Do**: Label = 1 if ticker’s close increases ≥ **k%** within **t** days after **trade_date** (e.g., k=5%, t=20 trading days). Tuneable via CLI.
  * **Accept**: Script generates (X, y) with N>10k rows from DB.

* [ ] **ML-3 | Train baseline**

  * **Files**: `backend/app/ml/train.py`, `backend/app/ml/evaluate.py`
  * **Do**: Train Logistic Regression or XGBoost (if available). Save:

    * `artifacts/model.joblib`
    * `artifacts/metrics.json` (AUC, PR-AUC, hit@K)
  * **Accept**: Reproducible run with fixed `--seed`; `metrics.json` saved.

* [ ] **ML-4 | Signal service + API**

  * **Files**: `backend/app/services/signal_service.py`, `backend/app/models/signal.py`, `backend/app/api/routes_signals.py`
  * **Do**:

    * `POST /signals/score`: input = list of recent filings (or `ticker` to fetch last N); output = probability + top-k reasons (feature contributions via permutation or model-specific importance).
    * `GET /signals/top`: returns ranked tickers for last X days.
  * **Accept**: Responses include `confidence`, `reasoning[]`, timestamps.

* [ ] **ML-5 | Scheduled refresh**

  * **Files**: `backend/app/main.py` (APSheduler), or cron
  * **Do**: Nightly: run `scrape.py --mode update`, then `train.py` weekly.
  * **Accept**: Logs show completed runs; artifacts rotate by date.

---

### [Frontend] M3 — App UI

* [ ] **F-1 | Next.js + Tailwind bootstrap**

  * **Files**: `frontend/` scaffolding
  * **Do**: Init Next.js (App Router), Tailwind, base theme.
  * **Accept**: `npm run dev` shows branded landing.

* [ ] **F-2 | Design system bits**

  * **Files**: `frontend/components/{Nav,Cards,TradeTable,SignalBadge,Charts,Filters}.tsx`
  * **Do**: Card, table, badge, time-range selector, mini-charts.
  * **Accept**: Components story or demo page renders.

* [ ] **F-3 | API client**

  * **Files**: `frontend/lib/api.ts`, `frontend/lib/types.ts`
  * **Do**: Wrap calls to `/trades`, `/companies`, `/insiders`, `/signals`.
  * **Accept**: TS types match backend schemas; errors handled.

* [ ] **F-4 | Pages**

  * **Files**:

    * `app/page.tsx`: **Landing** with your playful blurb + CTA
    * `app/dashboard/page.tsx`: KPIs (last 7/30d buys vs sells), recent large buys, top signals
    * `app/ticker/[symbol]/page.tsx`: company overview, recent filings table, price chart (placeholder if no market API)
    * `app/insider/[name]/page.tsx`: insider history, hit-rate, recent actions
  * **Accept**: All pages load real data from backend; client-side filters work.

* [ ] **F-5 | Charts & UX Polish**

  * **Files**: `components/Charts.tsx`, `components/Filters.tsx`
  * **Do**: Time-series chart of buys/sells; signal confidence bars; sticky filters.
  * **Accept**: 60fps scrolling; no layout shift on fetch.

---


## API Contract (v1)

* `GET /healthz` → `{status: "ok"}`
* `GET /trades?limit=&offset=&ticker=&insider_name=&trade_type=&flag=&date_from=&date_to=&min_value_usd=`
* `GET /companies/{ticker}`
* `GET /insiders/{name}`
* `GET /signals/top?window_days=30&limit=50`
* `POST /signals/score`

  ```json
  {
    "ticker": "AAPL",
    "lookback_days": 30
  }
  ```

  **or**

  ```json
  {
    "filings": [
      {
        "ticker": "AAPL",
        "trade_date": "2024-06-10",
        "insider_role": "CEO",
        "price": 188.5,
        "quantity": 50000,
        "ownership_after": 0.012
      }
    ]
  }
  ```

  **Response**

  ```json
  {
    "generated_at": "2025-09-25T12:00:00Z",
    "signals": [
      {
        "ticker": "AAPL",
        "score": 0.81,
        "confidence": "high",
        "reasons": [
          "Large CEO purchase vs 90d baseline",
          "Price near 30d SMA at buy",
          "Company buy ratio > 0.7 in last 60d"
        ]
      }
    ]
  }
  ```

---

## Commands

**Backend dev**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Train baseline**

```bash
python -m app.ml.train --k_pct 5 --horizon_days 20 --seed 42
python -m app.ml.evaluate --artifact app/ml/artifacts/model.joblib
```

**Scrape (incremental)**

```bash
python scrape.py --mode update --log-level INFO
```

**Frontend dev**

```bash
cd frontend
npm i
npm run dev
```

**Docker (dev)**

```bash
docker compose up --build
```

---

## Acceptance Demo (end of M3)

* Load `/dashboard`: see KPIs, recent large buys, top model signals
* Navigate to `/ticker/AAPL`: recent filings table + basic chart + company aggregates
* Open `/insider/[name]`: insider stats & last trades
* Hit `/signals/top`: returns ranked tickers with reasons
* Trigger `train.py`: artifact saved; `/signals/top` updated after restart

---

## Notes & Gotchas

* Use your existing `database.py` read/query helpers inside `trade_service.py` to avoid duplicate logic.
* Keep the model **simple and reproducible** first; log data version + feature config in `artifacts/`.
* If market price data isn’t integrated yet, compute label using your stored performance metrics or a cached price file; otherwise stub labels for demo and mark with `label_source: "stub"`.

