
import logging
from datetime import datetime, timezone

from fastapi import (
    FastAPI,
    Depends,
    Request,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app import models

from app.routes.auth import router as auth_router
from app.routes.security_events import router as security_events_router
from app.routes.incident import router as incidents_router
from app.routes.threat_intelligence import (
    router as threat_intelligence_router,
)
from app.routes.audit_logs import router as audit_logs_router
from app.routes.alerts import router as alerts_router
from app.routes.dashboard import router as dashboard_router
from app.routes.mitre import router as mitre_router
from app.routes.anomaly import router as anomaly_router
from app.routes.reports import router as reports_router

from app.security.rate_limit import rate_limit


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SentinelX Security Platform",
    description=(
        "AI-Assisted Security Monitoring and "
        "Incident Response Platform"
    ),
    version="1.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://sentinelx-frontend-29n4.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response


# Preserve intentional HTTP errors (401, 403, 404, etc.)
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


# Handle unexpected errors without exposing internal details
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logging.getLogger(__name__).error(
        "Unhandled error processing %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": (
                "Something went wrong while processing the request."
            ),
        },
    )


# Register API routers
app.include_router(auth_router)
app.include_router(security_events_router)
app.include_router(incidents_router)
app.include_router(threat_intelligence_router)
app.include_router(audit_logs_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(mitre_router)
app.include_router(anomaly_router)
app.include_router(reports_router)


# Root endpoint
@app.get("/", dependencies=[Depends(rate_limit)])
def root():
    return {
        "application": "SentinelX",
        "message": "Security Monitoring Platform is running",
        "status": "online",
    }


# Health endpoint
@app.get("/health", dependencies=[Depends(rate_limit)])
def health_check():
    return {
        "status": "healthy",
        "service": "SentinelX API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }