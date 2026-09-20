"""
FastAPI Application Entrypoint for Healthcare Blockchain DSA Capstone.

Assembles all route modules, configures CORS middleware, initializes
in-memory DSA state on startup, and provides OpenAPI documentation at /docs.
"""

import sys
import os
from contextlib import asynccontextmanager

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.state import AppState
from backend.routes import (
    auth,
    patients,
    encounters,
    claims,
    tamper,
    blockchain,
    audit,
    benchmark
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to initialize DSA structures on startup.
    """
    print("[BACKEND] Initializing In-Memory CustomHashTable and Blockchain Ledger...")
    state = AppState.get_instance()
    state.initialize()
    print(f"[BACKEND] Ready. Indexed {len(state.patient_id_table)} patients and {len(state.blockchain.chain)} blocks.")
    yield


app = FastAPI(
    title="Healthcare Record Integrity & Cross-Hospital Sharing API",
    description=(
        "Local Educational Blockchain Ledger Prototype using SHA-256 and Merkle Trees. "
        "Demonstrates decentralized healthcare verification across multiple hospitals and insurance payers."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS) for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API Routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(encounters.router)
app.include_router(claims.router)
app.include_router(tamper.router)
app.include_router(blockchain.router)
app.include_router(audit.router)
app.include_router(benchmark.router)


@app.get("/", tags=["System Root"])
def root():
    """
    Root system status endpoint.
    """
    state = AppState.get_instance()
    return {
        "project": "Healthcare Record Integrity and Medical Data Sharing using SHA-256 and Merkle Trees",
        "scope": "College DSA Capstone Functional Prototype",
        "api_documentation": "/docs",
        "interactive_redoc": "/redoc",
        "status": "OPERATIONAL",
        "patients_indexed": len(state.patient_id_table),
        "blockchain_height": len(state.blockchain.chain),
        "supported_roles": ["HOSPITAL", "INSURANCE", "ADMIN"],
        "patient_login_supported": False
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
