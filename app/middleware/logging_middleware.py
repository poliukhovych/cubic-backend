import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log information"""
        
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract request information
        method = request.method
        url = str(request.url)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {method} {url}",
            extra={
                "request_id": request_id,
                "method": method,
                "endpoint": request.url.path,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "query_params": dict(request.query_params),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Request completed: {method} {url} - Status: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code,
                    "duration": round(process_time * 1000, 2),  # in milliseconds
                }
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            
            return response
            
        except Exception as exc:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {method} {url} - Error: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "endpoint": request.url.path,
                    "duration": round(process_time * 1000, 2),
                    "error_type": type(exc).__name__,
                },
                exc_info=True
            )
            
            # Re-raise the exception to be handled by error middleware
            raise exc
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        
        return "Unknown"
