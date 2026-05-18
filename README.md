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

   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/health
   ```

   With Postgres running via Compose, `/health` should report `"database": "ok"`.

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
| `API_KEY` | Auto-generated (not enforced yet) |
| `ENVIRONMENT` | `production` |

HTTPS is provided by Render; no extra TLS setup is required for the web service.

## Project layout

```
app/
  main.py           # FastAPI app and routes
  config.py         # Settings from environment
  db/database.py    # SQLAlchemy engine and health check
  templates/        # Dashboard HTML
seed/               # Future load seed scripts
Dockerfile
docker-compose.yml
render.yaml
requirements.txt
```

## Roadmap

Planned in later iterations (not in this scaffold):

- Load CRUD API and seed data (`load_id`, origin, destination, rates, etc.)
- HappyRobot inbound agent integration (web call trigger)
- FMCSA carrier verification (MC number)
- Negotiation flow (up to 3 counter-offers) and mock transfer message
- Call extraction, outcome classification, and sentiment
- API key authentication on all endpoints
- Dashboard metrics (calls, outcomes, negotiation stats, sentiment)

## License

Private challenge repository.
