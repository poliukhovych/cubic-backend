import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger
from app.core.deps import get_current_user_id

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
        
        user_id = await self._get_user_id_for_logging(request)
        
        start_time = time.time()
        log_extra = {
            "request_id": request_id,
            "method": method,
            "endpoint": request.url.path,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "query_params": dict(request.query_params),
        }
        
        # Add user ID to log context if available
        if user_id:
            log_extra["user_id"] = user_id
        
        logger.info(
            f"Request started: {method} {url}",
            extra=log_extra
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            response_log_extra = {
                "request_id": request_id,
                "method": method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "duration": round(process_time * 1000, 2),  # in milliseconds
            }
            
            # Add user ID to response log if available
            if user_id:
                response_log_extra["user_id"] = user_id
            
            logger.info(
                f"Request completed: {method} {url} - Status: {response.status_code}",
                extra=response_log_extra
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            
            return response
            
        except Exception as exc:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time
            
            # Log error
            error_log_extra = {
                "request_id": request_id,
                "method": method,
                "endpoint": request.url.path,
                "duration": round(process_time * 1000, 2),
                "error_type": type(exc).__name__,
            }
            
            # Add user ID to error log if available
            if user_id:
                error_log_extra["user_id"] = user_id
            
            logger.error(
                f"Request failed: {method} {url} - Error: {str(exc)}",
                extra=error_log_extra,
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
    
    async def _get_user_id_for_logging(self, request: Request) -> Optional[str]:
        """
        Extract user ID for logging purposes.
        This method safely extracts user ID without raising exceptions.
        """
        try:
            # Call the user ID extraction function directly
            user_id = await get_current_user_id(request, None)
            return user_id
        except Exception:
            # If user extraction fails, continue without user ID
            # This ensures logging doesn't break if auth is not properly configured
            return None
