"""
Comprehensive logging system for Bolaquent application
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import request, session


def setup_logging(app):
    """Configure comprehensive logging for the application"""

    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure different log levels and files
    log_configs = [
        ("app.log", logging.INFO, "general"),
        ("auth.log", logging.INFO, "auth"),
        ("errors.log", logging.ERROR, "errors"),
        ("demo.log", logging.INFO, "demo"),
        ("debug.log", logging.DEBUG, "debug"),
    ]

    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s (%(pathname)s:%(lineno)d): " "%(message)s"
    )

    simple_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Configure Flask app logging
    if not app.debug:
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)

    # Create handlers for different log types
    for log_file, level, logger_name in log_configs:
        log_path = os.path.join(logs_dir, log_file)

        # Rotating file handler (10MB max, keep 5 backups)
        handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        handler.setLevel(level)
        handler.setFormatter(detailed_formatter)

        # Create specific logger
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(level)

        # Also add to Flask app logger for errors
        if logger_name == "errors":
            app.logger.addHandler(handler)

    return logging.getLogger("general")


def log_auth_attempt(username, age, success, error=None, session_type="regular"):
    """Log authentication attempts"""
    auth_logger = logging.getLogger("auth")

    user_info = {
        "username": username,
        "age": age,
        "session_type": session_type,
        "ip": request.remote_addr if request else "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown") if request else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
    }

    if success:
        auth_logger.info(f"Successful login: {user_info}")
    else:
        auth_logger.warning(f"Failed login: {user_info}, Error: {error}")


def log_demo_access(tier_name, tier_id, access_method="direct"):
    """Log demo access attempts"""
    demo_logger = logging.getLogger("demo")

    demo_info = {
        "tier_name": tier_name,
        "tier_id": tier_id,
        "access_method": access_method,
        "ip": request.remote_addr if request else "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown") if request else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
    }

    demo_logger.info(f"Demo access: {demo_info}")


def log_error(error, context="general"):
    """Log application errors"""
    error_logger = logging.getLogger("errors")

    error_info = {
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "url": request.url if request else "unknown",
        "method": request.method if request else "unknown",
        "ip": request.remote_addr if request else "unknown",
        "session": dict(session) if session else {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    error_logger.error(f"Application error: {error_info}")


def log_request(endpoint, method="GET", user=None):
    """Log application requests"""
    general_logger = logging.getLogger("general")

    request_info = {
        "endpoint": endpoint,
        "method": method,
        "user": user or session.get("username", "anonymous") if session else "anonymous",
        "ip": request.remote_addr if request else "unknown",
        "timestamp": datetime.utcnow().isoformat(),
    }

    general_logger.info(f"Request: {request_info}")


def log_debug(message, context="debug"):
    """Log debug information"""
    debug_logger = logging.getLogger("debug")

    debug_info = {
        "message": message,
        "context": context,
        "session": dict(session) if session else {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    debug_logger.debug(f"Debug: {debug_info}")
