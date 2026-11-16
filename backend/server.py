import asyncio
import logging
import os
from contextlib import suppress
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

try:
    from backend.clerk_auth import clerk_router
except ModuleNotFoundError:
    from clerk_auth import clerk_router

from genova.api import router as genova_router
from genova.auth import RETIRED_ROLES
from genova.db import client, db
from genova.feedback import router as feedback_router
from genova.genetics import GeneticsInputError
from genova.i18n import LANGS, t

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("genova")

INDEXES: dict[str, list[IndexModel]] = {
    "analyses": [IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_created"),
                 IndexModel([("user_id", ASCENDING), ("analysis_type", ASCENDING), ("created_at", DESCENDING)],
                            name="user_kind_created")],
    "users": [IndexModel([("user_id", ASCENDING)], name="user_id", unique=True)],
    "confirmations_pregnancy": [IndexModel([("analysis_id", ASCENDING)], name="analysis_id", unique=True)],
    "confirmations_birth": [IndexModel([("analysis_id", ASCENDING)], name="analysis_id", unique=True)],
    "ratings": [IndexModel([("analysis_id", ASCENDING)], name="analysis_id", unique=True)],
    "usage_daily": [IndexModel([("user_id", ASCENDING), ("kind", ASCENDING), ("day", ASCENDING)], name="user_kind_day",
                               unique=True)],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:
            try:
                await db[collection].create_indexes([model])
            except PyMongoError as exc:
                logger.error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)


app = FastAPI(title="GENOVA AI API", version="1.0.0")
app.include_router(genova_router)
app.include_router(feedback_router)
app.include_router(clerk_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def _lang(request: Request) -> str:
    lang = request.query_params.get("lang", "en")
    return lang if lang in LANGS else "en"


@app.exception_handler(GeneticsInputError)
async def genetics_error(request: Request, exc: GeneticsInputError):
    code = str(exc)
    return JSONResponse(status_code=400, content={"detail": {"code": code, "message": t(code, _lang(request))}})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": {"code": "validation_error", "errors": errors}})


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
async def startup():
    app.state.index_task = asyncio.create_task(ensure_indexes())
    for old, new in RETIRED_ROLES.items():
        await db.users.update_many({"role": old}, {"$set": {"role": new}})


@app.on_event("shutdown")
async def shutdown():
    app.state.index_task.cancel()
    with suppress(asyncio.CancelledError):
        await app.state.index_task
    client.close()
