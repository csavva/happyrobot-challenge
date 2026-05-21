from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import check_db_connection
from app.db.init_db import init_database
from app.dependencies.db import get_db_session
from app.routers.analytics import router as analytics_router
from app.routers.calls import router as calls_router
from app.routers.fmcsa import router as fmcsa_router
from app.routers.loads import router as loads_router
from app.services.analytics import get_call_analytics


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Inbound Carrier Sales",
    description="HappyRobot FDE Technical Challenge — inbound carrier load sales automation",
    version="0.1.0",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app.include_router(fmcsa_router)
app.include_router(loads_router)
app.include_router(calls_router)
app.include_router(analytics_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "database": check_db_connection(),
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db_session),
) -> HTMLResponse:
    try:
        analytics = get_call_analytics(db)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Unable to load analytics") from exc
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"analytics": analytics},
    )
