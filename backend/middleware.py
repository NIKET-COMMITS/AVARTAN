"""
Security Middleware - Request/Response Security

Prevents:
- Suspicious request patterns
- Path traversal attacks
- Oversized requests
- Adds security headers
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.logger import log_security_event, logger
import time


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security checks for every request
    """
    
    async def dispatch(self, request: Request, call_next):
        # Record request start time
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get path
        path = request.url.path
        
        # Prevent path traversal attacks
        if ".." in path or "\\x" in path:
            log_security_event(
                "SUSPICIOUS_PATH_TRAVERSAL",
                details=f"Path: {path} | IP: {client_ip}"
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"detail": "Invalid request"},
                status_code=400
            )
        
        # Prevent extremely large requests
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:
            log_security_event(
                "OVERSIZED_REQUEST",
                details=f"Size: {content_length} | IP: {client_ip}"
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"detail": "Request too large"},
                status_code=413
            )
        
        # Process request
        response = await call_next(request)
        
        # Record response time
        process_time = time.time() - start_time
        
        # Log slow requests
        if process_time > 5:
            logger.warning(
                f"SLOW_REQUEST: {request.method} {path} "
                f"took {process_time:.2f}s"
            )
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response