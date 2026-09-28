"""
FastAPI application factory.

Run with:
    uvicorn backend.app.main:app --reload --port 8000
"""

from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.routers import (
    health,
    overview,
    waste,
    demand,
    promotions,
    events,
    model_router,
    insights,
    recommendations,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model at startup so the first request is not slow.
    try:
        from backend.app.services.recommendation_service import get_model
        get_model()
    except FileNotFoundError:
        # Model not yet trained — API still starts; prediction endpoints
        # return 503 individually.
        pass
    yield


app = FastAPI(
    title="ServeCycle API",
    description="Food waste analysis and preparation planning for catering operations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log the full error server-side; return a generic message to the client.
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Check server logs."},
    )


app.include_router(health.router)
app.include_router(overview.router)
app.include_router(waste.router)
app.include_router(demand.router)
app.include_router(promotions.router)
app.include_router(events.router)
app.include_router(model_router.router)
app.include_router(insights.router)
app.include_router(recommendations.router)
