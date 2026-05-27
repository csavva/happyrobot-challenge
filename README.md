# Inbound Carrier Sales

HappyRobot **FDE Technical Challenge** — inbound carrier load sales automation. Carriers are verified via FMCSA, loads are matched by reference number, call outcomes are logged from the voice agent, and metrics are shown on a custom dashboard.

**Stack:** FastAPI · PostgreSQL · Docker · [Render](https://render.com/) Blueprint

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Set `FMCSA_WEB_KEY` in `.env` for carrier verification ([FMCSA QCMobile](https://mobile.fmcsa.dot.gov/QCDevsite/)).

| URL | Auth |
|-----|------|
| [/dashboard](http://localhost:8000/dashboard) | — |
| [/analytics/calls](http://localhost:8000/analytics/calls) | — |
| [/docs](http://localhost:8000/docs) | — |
| `/health` | — |
| `/fmcsa-validate?mc_number=…` | `X-API-Key` |
| `/loads-search?reference_number=…` | `X-API-Key` |
| `POST /calls` | `X-API-Key` |

Local API key default: `dev-change-me` (`API_KEY` in `.env`).

## API

### GET `/fmcsa-validate`

Query param: `mc_number`. Returns eligibility and carrier name from FMCSA.

### GET `/loads-search`

Query param: `reference_number` (e.g. `HRL2847`, `HRB1092`, `HRM3310`, `HRD5501`, `HRC7720`).

### POST `/calls`

HappyRobot post-call webhook. JSON body:

| Field | Values |
|-------|--------|
| `classification` | `Success`, `Rate too high`, `Not interested` |
| `booking_decision` | `yes` (with Success), `no` (with declines) |
| `call_sentiment` | `Positive`, `Negative`, `Neutral` |
| `reference_number` | Load reference |
| `mc_number` | Carrier MC number |
| `decline_reason` | Text if declined; `""` otherwise |
| `call_duration` | Seconds (string or number) |
| `carrier_initial_offer` | Optional initial carrier rate |
| `final_agreed_rate` | Optional agreed rate |
| `num_negotiation_rounds` | Optional; `0` if no negotiation |

```bash
curl -X POST http://localhost:8000/calls \
  -H "X-API-Key: dev-change-me" \
  -H "Content-Type: application/json" \
  -d '{"classification":"Success","reference_number":"HRL2847","mc_number":"145300","decline_reason":"","booking_decision":"yes","call_sentiment":"Positive","call_duration":"80"}'
```

### GET `/analytics/calls`

JSON summary: totals, success rate, classification and sentiment breakdowns, `avg_final_rate`, `avg_negotiation_rounds`, recent calls.

## Deploy on Render

1. Push to GitHub and create a **Blueprint** from [`render.yaml`](render.yaml) (web service + Postgres).
2. Set `FMCSA_WEB_KEY` in the web service environment.
3. Use the generated `API_KEY` as `X-API-Key` in HappyRobot HTTP tools.
4. Open `https://<your-service>.onrender.com/dashboard`.

Tables and seed data load on first startup when the database is empty.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `API_KEY` | Sent as `X-API-Key` on protected routes |
| `FMCSA_WEB_KEY` | FMCSA QCMobile API key |
| `ENVIRONMENT` | `development` or `production` |
