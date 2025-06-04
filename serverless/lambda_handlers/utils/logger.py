"""
Structured logging utility for Mind Map serverless application.
Implements the logging strategy defined in LOGGING_STRATEGY.md
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os


class StructuredLogger:
    """
    Centralized logging utility that implements structured logging format
    for consistent log analysis and monitoring across all Lambda functions.
    """
    
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.logger = logging.getLogger(function_name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _create_log_entry(
        self,
        level: str,
        category: str,
        message: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create structured log entry following the defined format."""
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "category": category,
            "function_name": self.function_name,
            "environment": os.environ.get('AWS_LAMBDA_FUNCTION_VERSION', 'local'),
            "message": message
        }
        
        # Add optional fields if provided
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
        if user_id:
            log_entry["user_id"] = user_id
        if request_id:
            log_entry["request_id"] = request_id
        if additional_data:
            log_entry.update(additional_data)
            
        return log_entry
    
    def request(self, method: str, path: str, correlation_id: str, user_id: Optional[str] = None, 
               body: Optional[Dict] = None, headers: Optional[Dict] = None):
        """Log incoming requests."""
        additional_data = {
            "http_method": method,
            "path": path,
            "body_size": len(json.dumps(body)) if body else 0
        }
        if headers:
            additional_data["headers"] = {k: v for k, v in headers.items() 
                                       if k.lower() not in ['authorization', 'cookie']}
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="REQUEST",
            message=f"Incoming {method} request to {path}",
            correlation_id=correlation_id,
            user_id=user_id,
            additional_data=additional_data
        )
        self.logger.info(json.dumps(log_entry))
    
    def response(self, status_code: int, correlation_id: str, response_size: int = 0, 
                execution_time_ms: Optional[float] = None):
        """Log outgoing responses."""
        additional_data = {
            "status_code": status_code,
            "response_size": response_size
        }
        if execution_time_ms:
            additional_data["execution_time_ms"] = execution_time_ms
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="RESPONSE",
            message=f"Response sent with status {status_code}",
            correlation_id=correlation_id,
            additional_data=additional_data
        )
        self.logger.info(json.dumps(log_entry))
    
    def database_operation(self, operation: str, table_name: str, correlation_id: str,
                          execution_time_ms: Optional[float] = None, item_count: Optional[int] = None,
                          consumed_capacity: Optional[float] = None):
        """Log database operations."""
        additional_data = {
            "operation": operation,
            "table_name": table_name
        }
        if execution_time_ms:
            additional_data["execution_time_ms"] = execution_time_ms
        if item_count is not None:
            additional_data["item_count"] = item_count
        if consumed_capacity:
            additional_data["consumed_capacity"] = consumed_capacity
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="DATABASE",
            message=f"DynamoDB {operation} operation on {table_name}",
            correlation_id=correlation_id,
            additional_data=additional_data
        )
        self.logger.info(json.dumps(log_entry))
    
    def s3_operation(self, operation: str, bucket: str, key: str, correlation_id: str,
                    execution_time_ms: Optional[float] = None, object_size: Optional[int] = None):
        """Log S3 operations."""
        additional_data = {
            "operation": operation,
            "bucket": bucket,
            "key": key
        }
        if execution_time_ms:
            additional_data["execution_time_ms"] = execution_time_ms
        if object_size:
            additional_data["object_size"] = object_size
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="S3",
            message=f"S3 {operation} operation on {bucket}/{key}",
            correlation_id=correlation_id,
            additional_data=additional_data
        )
        self.logger.info(json.dumps(log_entry))
    
    def business_logic(self, message: str, correlation_id: str, operation: Optional[str] = None,
                      additional_data: Optional[Dict[str, Any]] = None):
        """Log business logic events."""
        data = {"business_operation": operation} if operation else {}
        if additional_data:
            data.update(additional_data)
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="BUSINESS",
            message=message,
            correlation_id=correlation_id,
            additional_data=data
        )
        self.logger.info(json.dumps(log_entry))
    
    def performance(self, operation: str, execution_time_ms: float, correlation_id: str,
                   memory_used_mb: Optional[float] = None, additional_metrics: Optional[Dict] = None):
        """Log performance metrics."""
        additional_data = {
            "operation": operation,
            "execution_time_ms": execution_time_ms
        }
        if memory_used_mb:
            additional_data["memory_used_mb"] = memory_used_mb
        if additional_metrics:
            additional_data.update(additional_metrics)
        
        log_entry = self._create_log_entry(
            level="INFO",
            category="PERFORMANCE",
            message=f"Performance metrics for {operation}",
            correlation_id=correlation_id,
            additional_data=additional_data
        )
        self.logger.info(json.dumps(log_entry))
    
    def security(self, event_type: str, message: str, correlation_id: str, user_id: Optional[str] = None,
                ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log security-related events."""
        additional_data = {
            "security_event_type": event_type
        }
        if ip_address:
            additional_data["ip_address"] = ip_address
        if user_agent:
            additional_data["user_agent"] = user_agent
        
        log_entry = self._create_log_entry(
            level="WARN",
            category="SECURITY",
            message=message,
            correlation_id=correlation_id,
            user_id=user_id,
            additional_data=additional_data
        )
        self.logger.warning(json.dumps(log_entry))
    
    def error(self, error_type: str, message: str, correlation_id: str, 
             stack_trace: Optional[str] = None, error_code: Optional[str] = None,
             additional_context: Optional[Dict[str, Any]] = None):
        """Log errors with full context."""
        additional_data = {
            "error_type": error_type
        }
        if error_code:
            additional_data["error_code"] = error_code
        if stack_trace:
            additional_data["stack_trace"] = stack_trace
        if additional_context:
            additional_data.update(additional_context)
        
        log_entry = self._create_log_entry(
            level="ERROR",
            category="ERROR",
            message=message,
            correlation_id=correlation_id,
            additional_data=additional_data
        )
        self.logger.error(json.dumps(log_entry))


class PerformanceTracker:
    """Context manager for tracking operation performance."""
    
    def __init__(self, logger: StructuredLogger, operation: str, correlation_id: str):
        self.logger = logger
        self.operation = operation
        self.correlation_id = correlation_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time_ms = (time.time() - self.start_time) * 1000
            self.logger.performance(
                operation=self.operation,
                execution_time_ms=execution_time_ms,
                correlation_id=self.correlation_id
            )


def extract_correlation_id(event: Dict[str, Any]) -> str:
    """Extract or generate correlation ID from API Gateway event."""
    # Try to get from headers first
    headers = event.get('headers', {})
    correlation_id = headers.get('X-Correlation-ID') or headers.get('x-correlation-id')
    
    if not correlation_id:
        # Try to get from request context
        request_context = event.get('requestContext', {})
        correlation_id = request_context.get('requestId')
    
    if not correlation_id:
        # Generate new correlation ID
        import uuid
        correlation_id = str(uuid.uuid4())
    
    return correlation_id


def extract_user_id(event: Dict[str, Any]) -> Optional[str]:
    """Extract user ID from API Gateway event."""
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    # Try Cognito JWT claims
    claims = authorizer.get('claims', {})
    user_id = claims.get('sub')
    
    if not user_id:
        # Try other authorization methods
        user_id = authorizer.get('principalId')
    
    return user_id
