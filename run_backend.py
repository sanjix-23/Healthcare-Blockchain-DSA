"""
Runner Script for Healthcare Blockchain DSA REST API Backend.

Launches FastAPI on port 8000.
Interactive Swagger API documentation available at:
    http://127.0.0.1:8000/docs
"""

import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("HEALTHCARE BLOCKCHAIN DSA REST API BACKEND")
    print("=" * 70)
    print("Server URL                    : http://127.0.0.1:8000")
    print("Swagger OpenAPI Documentation : http://127.0.0.1:8000/docs")
    print("ReDoc API Documentation       : http://127.0.0.1:8000/redoc")
    print("System Status                 : http://127.0.0.1:8000/")
    print("=" * 70)
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)
