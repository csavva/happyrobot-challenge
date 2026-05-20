# Inbound Carrier Sales

Proof of concept for the HappyRobot **FDE Technical Challenge: Inbound Carrier Sales**. Freight brokers receive inbound calls from carriers looking to book loads; this system will vet carriers, match loads, negotiate pricing, and surface call metrics on a custom dashboard.

**Current status:** infrastructure scaffold only (Hello World API, placeholder dashboard, Docker, Render Postgres wiring). Business logic is not implemented yet.

## Stack

- **API:** [FastAPI](https://fastapi.tiangolo.com/)
- **Dashboard:** HTML5 templates (Jinja2), served by FastAPI
- **Database:** PostgreSQL (SQLAlchemy connectivity stub)
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
   | http://localhost:8000/dashboard | Placeholder metrics dashboard |
   | http://localhost:8000/docs | OpenAPI (Swagger UI) |
   | http://localhost:8000/fmcsa-validate?mc_number=123456 | FMCSA carrier eligibility check |
   | http://localhost:8000/loads-search?reference_number=HRL2847 | Load lookup by posting reference |

   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/health
   curl -H "X-API-Key: dev-change-me" "http://localhost:8000/fmcsa-validate?mc_number=1515"
   curl -H "X-API-Key: dev-change-me" "http://localhost:8000/loads-search?reference_number=HRL2847"
   ```

   With Postgres running via Compose, `/health` should report `"database": "ok"`.

   Protected routes require the `X-API-Key` header (value from `API_KEY` in `.env`).

   **Seed reference numbers** (3 letters + 4 digits, auto-loaded on first startup): `HRL2847`, `HRB1092`, `HRM3310`, `HRD5501`, `HRC7720`.

## Deploy on Render

1. Push this repository to GitHub (or GitLab/Bitbucket).
2. In the [Render Dashboard](https://dashboard.render.com/), choose **New → Blueprint**.
3. Connect the repository. Render reads [`render.yaml`](render.yaml) and provisions:
   - **Web service** `happyrobot-carrier-sales` (Docker)
   - **PostgreSQL** `happyrobot-db` (`carrier_sales` database)
4. After deploy, open the service URL. Health checks use `GET /health`.

Environment variables (set by Blueprint):

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Linked from `happyrobot-db` |
| `API_KEY` | Auto-generated; required as `X-API-Key` header on protected routes |
| `ENVIRONMENT` | `production` |
| `FMCSA_WEB_KEY` | Set manually in Render (from [FMCSA QCMobile](https://mobile.fmcsa.dot.gov/QCDevsite/)) |

HTTPS is provided by Render; no extra TLS setup is required for the web service.

## Project layout

```
app/
  main.py           # FastAPI app and routes
  config.py         # Settings from environment
  db/database.py    # SQLAlchemy engine and health check
  templates/        # Dashboard HTML
seed/               # Optional manual seed runner (`python -m seed.seed_loads`)
app/seed/loads.json # Demo load dataset (auto-seeded on startup when DB is empty)
Dockerfile
docker-compose.yml
render.yaml
requirements.txt
```

## Roadmap

Planned in later iterations (not in this scaffold):

- ~~Load search by reference~~ — `GET /loads-search?reference_number=...` (seed data in `app/seed/loads.json`)
- Load search by lane / equipment (no reference number)
- HappyRobot inbound agent integration (web call trigger)
- ~~FMCSA carrier verification (MC number)~~ — `GET /fmcsa-validate?mc_number=...` (requires `FMCSA_WEB_KEY`)
- Negotiation flow (up to 3 counter-offers) and mock transfer message
- Call extraction, outcome classification, and sentiment
- API key authentication on remaining endpoints
- Dashboard metrics (calls, outcomes, negotiation stats, sentiment)

## License

Private challenge repository.
