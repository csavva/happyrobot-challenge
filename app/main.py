from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.database import check_db_connection

app = FastAPI(
    title="Inbound Carrier Sales",
    description="HappyRobot FDE Technical Challenge — inbound carrier load sales automation",
    version="0.1.0",
)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


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
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )
