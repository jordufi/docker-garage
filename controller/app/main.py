"""
Home Server Orchestrator — FastAPI entry point.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

# ─── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

# ─── App ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Home Server Orchestrator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# CORS — permissive for home LAN; tighten for internet exposure
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
