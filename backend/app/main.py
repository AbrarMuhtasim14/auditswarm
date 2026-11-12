"""
Main FastAPI application entrypoint for AuditSwarm.
Re-exports the application instance from server.py for standard uvicorn invocations:
    uvicorn app.main:app --reload
"""
try:
    from backend.app.server import app
except ImportError:
    from app.server import app

__all__ = ["app"]
