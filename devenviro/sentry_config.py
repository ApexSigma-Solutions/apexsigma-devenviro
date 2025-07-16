"""
Sentry configuration for devenviro application.
"""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from typing import Optional, Dict, Any


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "development",
    sample_rate: float = 1.0,
    enable_tracing: bool = True,
    enable_profiling: bool = True,
    debug: bool = False
):
    """
    Initialize Sentry SDK with appropriate configuration.
    
    Args:
        dsn: Sentry DSN URL
        environment: Environment (development, staging, production)
        sample_rate: Sample rate for error reporting (0.0 to 1.0)
        enable_tracing: Whether to enable performance tracing
        enable_profiling: Whether to enable profiling
        debug: Whether to enable debug mode
    """
    if not dsn:
        dsn = os.getenv("SENTRY_DSN")
    
    if not dsn:
        print("Warning: No Sentry DSN provided. Sentry will not be initialized.")
        return
    
    # Configure integrations
    integrations = [
        FastApiIntegration(),
        StarletteIntegration(),
        LoggingIntegration(
            level=None,  # Capture all log levels
            event_level=None  # Don't automatically create events from logs
        ),
        StdlibIntegration()
    ]
    
    # Adjust sample rates for different environments
    traces_sample_rate = 1.0 if environment == "development" else 0.1
    profiles_sample_rate = 1.0 if environment == "development" else 0.1
    
    if not enable_tracing:
        traces_sample_rate = 0.0
    if not enable_profiling:
        profiles_sample_rate = 0.0
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=integrations,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=True,  # Include user IP and headers
        attach_stacktrace=True,  # Attach stack traces to messages
        debug=debug,
        release=os.getenv("SENTRY_RELEASE"),
        before_send=_before_send_filter,
    )
    
    print(f"Sentry initialized for environment: {environment}")


def _before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.
    Can be used to exclude certain errors or add additional context.
    """
    # Example: Filter out specific exceptions
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, KeyboardInterrupt):
            return None
    
    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['component'] = 'devenviro'
    
    return event


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture a message with Sentry.
    
    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        **kwargs: Additional context
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_context(key, value)
        sentry_sdk.capture_message(message, level=level)  # type: ignore


def capture_exception(exception: Exception, **kwargs):
    """
    Capture an exception with Sentry.
    
    Args:
        exception: The exception to capture
        **kwargs: Additional context
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in kwargs.items():
            scope.set_context(key, value)
        sentry_sdk.capture_exception(exception)


def set_user_context(user_id: str, username: Optional[str] = None, email: Optional[str] = None):
    """
    Set user context for Sentry events.
    
    Args:
        user_id: User ID
        username: Username (optional)
        email: Email (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "email": email
    })


def set_tag(key: str, value: str):
    """
    Set a tag for Sentry events.
    
    Args:
        key: Tag key
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)


def set_context(key: str, context: Dict[str, Any]):
    """
    Set context for Sentry events.
    
    Args:
        key: Context key
        context: Context dictionary
    """
    sentry_sdk.set_context(key, context)