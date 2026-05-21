# Inbound Carrier Sales

Proof of concept for the HappyRobot **FDE Technical Challenge: Inbound Carrier Sales**. Freight brokers receive inbound calls from carriers looking to book loads; this system vets carriers (FMCSA), matches loads, logs call outcomes, and surfaces metrics on a custom dashboard.

## Stack

- **API:** [FastAPI](https://fastapi.tiangolo.com/)
- **Dashboard:** HTML5 templates (Jinja2), server-rendered analytics
- **Database:** PostgreSQL (SQLAlchemy)
- **Containers:** Docker + Docker Compose (local), [Render](https://render.com/) Blueprint (production)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) [Render](https://render.com/) account for deployment

## Local development

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Start the stack:

   ```bash
   docker compose up --build
   ```

3. Verify endpoints:

   | URL | Description |
   |-----|-------------|
   | http://localhost:8000/ | Hello World JSON |
   | http://localhost:8000/health | Liveness + database connectivity |
   | http://localhost:8000/dashboard | Call analytics dashboard (HTML) |
   | http://localhost:8000/analytics/calls | Call analytics (JSON) |
   | http://localhost:8000/docs | OpenAPI (Swagger UI) |
   | http://localhost:8000/fmcsa-validate?mc_number=123456 | FMCSA carrier eligibility (API key) |
   | http://localhost:8000/loads-search?reference_number=HRL2847 | Load lookup (API key) |

   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/analytics/calls
   curl -H "X-API-Key: dev-change-me" "http://localhost:8000/fmcsa-validate?mc_number=1515"
   curl -H "X-API-Key: dev-change-me" "http://localhost:8000/loads-search?reference_number=HRL2847"
   curl -X POST http://localhost:8000/calls \
     -H "X-API-Key: dev-change-me" \
     -H "Content-Type: application/json" \
     -d '{"classification":"Not interested","reference_number":"HRB1092","mc_number":"MC123456","decline_reason":"timing","booking_decision":"no","call_duration":"120"}'
   ```

   Protected routes require the `X-API-Key` header (value from `API_KEY` in `.env`).

   **Seed load reference numbers** (3 letters + 4 digits): `HRL2847`, `HRB1092`, `HRM3310`, `HRD5501`, `HRC7720`.

   Demo **call** rows are seeded when the `calls` table is empty (see `app/seed/calls.json`).

## POST /calls (HappyRobot post-call tool)

| Field | Values |
|-------|--------|
| `classification` | `Success`, `Rate too high`, `Not interested` |
| `booking_decision` | `yes` (required for Success), `no` (required for declines) |
| `reference_number` | Load reference from posting |
| `mc_number` | Carrier MC number |
| `decline_reason` | Free text when declined; empty string if N/A |
| `call_duration` | Duration in seconds (string or number, e.g. `"120"`) |

## Deploy on Render

1. Push this repository to GitHub (or GitLab/Bitbucket).
2. In the [Render Dashboard](https://dashboard.render.com/), choose **New → Blueprint**.
3. Connect the repository. Render reads [`render.yaml`](render.yaml) and provisions the web service and Postgres.
4. After deploy, open `/dashboard`. The `calls` table is created on deploy via `create_all` (existing `loads` data is preserved).

Environment variables:

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Linked from Postgres |
| `API_KEY` | Auto-generated; use as `X-API-Key` on protected routes |
| `ENVIRONMENT` | `production` |
| `FMCSA_WEB_KEY` | Set manually ([FMCSA QCMobile](https://mobile.fmcsa.dot.gov/QCDevsite/)) |

## Project layout

```
app/
  main.py
  routers/          # fmcsa, loads, calls, analytics
  services/         # fmcsa client, analytics
  db/models.py      # Load, Call
  seed/             # loads.json, calls.json
  templates/        # dashboard.html
```

## Roadmap

- Load search by lane / equipment (no reference number)
- Negotiation flow (up to 3 counter-offers) and mock transfer message
- Sentiment on calls

## License

Private challenge repository.
