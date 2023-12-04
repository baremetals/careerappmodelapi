from typing import Any
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from career_app_model import __version__ as app_model_version

from app import __version__, schemas
from app.config import settings

router = APIRouter()


@router.get("/")
def index(request: Request) -> Any:
    """Basic HTML response."""
    body = (
        "<html>"
        "<body style='padding: 10px;'>"
        "<h1>Welcome to the API</h1>"
        "<div>"
        "Check the docs: <a href='/docs'>here</a>"
        "</div>"
        "</body>"
        "</html>"
    )

    return HTMLResponse(content=body)


@router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    healthy = schemas.Health(
        name=settings.PROJECT_NAME, api_version=__version__, app_model_version=app_model_version
    )

    return healthy.model_dump()

