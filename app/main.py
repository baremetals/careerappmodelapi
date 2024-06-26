from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.responses import PlainTextResponse
from app.routers import career, root, auth, admin, users
from app.config.settings import settings, setup_app_logging
import app.models.user as models
from app.config.database import engine
from sqlalchemy.orm import Session
from typing import Annotated
from app.config.database import get_db
from slowapi.errors import RateLimitExceeded

# setup logging as early as possible
setup_app_logging(config=settings)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
models.Base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session, Depends(get_db)]


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(exc: RateLimitExceeded):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        # allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    print("Middleware executed")
    headers = request.headers
    logger.info(f"Request headers: {headers}")

    response = await call_next(request)
    return response


app.include_router(root.router)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(career.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    # Use this for debugging purposes only
    logger.warning("Running in development mode. Do not run like this in production.")
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
