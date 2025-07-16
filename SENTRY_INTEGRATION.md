# Sentry Integration Documentation

## Overview

This document describes the comprehensive Sentry integration implemented for the devenviro project. Sentry provides real-time error tracking, performance monitoring, and user context for the cognitive collaboration system.

## Architecture

### Components

1. **Sentry Configuration Module** (`devenviro/sentry_config.py`)
   - Environment-specific configuration
   - Custom error filtering and context enhancement
   - Helper functions for message and exception capture

2. **FastAPI Application** (`devenviro/main.py`)
   - Main web application with Sentry integration
   - Global exception handlers
   - Health check and debugging endpoints

3. **Docker Deployment** (`docker-compose.yml`, `Dockerfile`)
   - Containerized deployment with Sentry configuration
   - Environment variable management

## Features

### Error Tracking
- **Automatic Exception Capture**: All unhandled exceptions are automatically sent to Sentry
- **Manual Error Reporting**: Developers can manually capture messages and exceptions
- **User Context**: User information is attached to error reports for better debugging
- **Request Context**: HTTP request details are included in error reports

### Performance Monitoring
- **Transaction Tracing**: API endpoint performance tracking
- **Profiling**: CPU and memory profiling (configurable)
- **Custom Metrics**: Application-specific performance metrics

### Environment Configuration
- **Development**: 100% sampling for comprehensive debugging
- **Production**: 10% sampling for performance optimization
- **Staging**: Configurable sampling rates

## Setup Instructions

### 1. Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Configure the following variables:

```env
# Environment Configuration
ENVIRONMENT=development  # or staging, production

# Sentry Configuration
SENTRY_DSN=https://3f4240883d9c2ac20e4d339d5aed2b6d@o4509669791760384.ingest.de.sentry.io/4509679484272720
SENTRY_RELEASE=v1.0.0  # Optional: for release tracking

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Other configuration...
```

### 2. Local Development

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run on a different port to avoid conflicts:
```bash
python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Docker Deployment

Start the complete stack:
```bash
docker-compose up -d
```

This will start:
- DevEnviro API server (port 8000)
- Qdrant vector database (port 6333)

### 4. Testing Integration

Run the Sentry integration tests:
```bash
python test_sentry.py
```

This will test:
- Sentry initialization
- Message capture
- Exception capture
- User context setting
- FastAPI endpoint integration

## API Endpoints

### Health Check
```
GET /health
```

Returns application health status including Sentry enablement.

### Error Testing
```
POST /test-error
{
  "error_type": "message|exception|http",
  "message": "Test error message",
  "user_id": "optional_user_id"
}
```

### Debug Endpoint
```
GET /sentry-debug
```

Triggers a test exception for Sentry validation.

### System Status
```
GET /system/status
```

Returns system monitoring information.

## Configuration Options

### Sentry Configuration (`devenviro/sentry_config.py`)

```python
init_sentry(
    dsn="your-sentry-dsn",
    environment="development",  # development, staging, production
    sample_rate=1.0,           # Error sampling rate
    enable_tracing=True,       # Performance tracing
    enable_profiling=True,     # CPU/memory profiling
    debug=False               # Debug mode
)
```

### Environment-Specific Settings

| Environment | Traces Sample Rate | Profiles Sample Rate | Debug Mode |
|-------------|-------------------|---------------------|------------|
| Development | 100% | 100% | Yes |
| Staging | 10% | 10% | No |
| Production | 10% | 10% | No |

## Usage Examples

### Manual Error Capture

```python
from devenviro.sentry_config import capture_message, capture_exception, set_user_context

# Set user context
set_user_context("user123", username="john_doe", email="john@example.com")

# Capture a message
capture_message("Something interesting happened", level="info")

# Capture an exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, custom_context={"operation": "risky_operation"})
```

### Context Enhancement

```python
from devenviro.sentry_config import set_tag, set_context

# Add tags for filtering
set_tag("feature", "memory_management")
set_tag("user_tier", "premium")

# Add structured context
set_context("ai_model", {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
})
```

## Integration with Existing Systems

### ErrorTracker Integration

The existing `ErrorTracker` class continues to work alongside Sentry:

```python
from devenviro.monitoring import ErrorTracker

error_tracker = ErrorTracker()

# This will log to both local files AND Sentry
try:
    operation()
except Exception as e:
    error_tracker.log_error(e, context={"operation": "memory_creation"})
    # Sentry capture happens automatically via global exception handler
```

### Memory Service Integration

```python
from devenviro.sentry_config import set_user_context, capture_message

@app.post("/memories")
async def create_memory(request: MemoryRequest):
    # Set user context for better error tracking
    set_user_context(request.user_id)
    
    try:
        # Your memory creation logic
        memory = create_memory_logic(request.content)
        
        # Log successful operations
        capture_message(f"Memory created for user {request.user_id}", level="info")
        
        return memory
    except Exception as e:
        # Exception will be automatically captured with user context
        raise HTTPException(status_code=500, detail="Memory creation failed")
```

## Monitoring and Alerts

### Sentry Dashboard

Access your Sentry dashboard at:
https://sentry.io/organizations/apexsigma/issues/

### Key Metrics to Monitor

1. **Error Rate**: Track application error frequency
2. **Performance**: API endpoint response times
3. **User Impact**: Users affected by errors
4. **Release Health**: Error rates by deployment version

### Recommended Alerts

Set up alerts for:
- Error rate exceeding 5%
- Performance degradation (95th percentile > 2s)
- New error types
- High-volume error spikes

## Security Considerations

### PII Handling

The current configuration includes `send_default_pii=True` for development. For production:

1. Review PII data being sent
2. Configure `before_send` filter to scrub sensitive data
3. Consider setting `send_default_pii=False` for production

### Access Control

- Sentry DSN should be treated as sensitive
- Use environment variables, not hardcoded values
- Rotate DSN keys periodically

## Troubleshooting

### Common Issues

1. **Sentry not initializing**
   - Check DSN configuration
   - Verify network connectivity
   - Check environment variables

2. **Missing context in errors**
   - Ensure user context is set before operations
   - Check custom context configuration

3. **Performance impact**
   - Reduce sampling rates in production
   - Disable profiling if not needed

### Debug Mode

Enable debug mode for verbose logging:

```python
init_sentry(debug=True)
```

This will show detailed Sentry SDK logs for troubleshooting.

## Future Enhancements

### Planned Features

1. **Custom Metrics**: Application-specific metrics
2. **Release Tracking**: Automated release tagging
3. **User Feedback**: In-app user feedback collection
4. **Advanced Filtering**: Custom error grouping and filtering
5. **Integration Expansion**: Additional AI service monitoring

### Performance Optimizations

1. **Sampling Strategy**: Dynamic sampling based on error type
2. **Batch Processing**: Batch error reporting for high-volume scenarios
3. **Local Caching**: Cache configuration for faster initialization

---

## Support

For issues or questions regarding Sentry integration:

1. Check the Sentry documentation: https://docs.sentry.io/
2. Review error logs in the Sentry dashboard
3. Test with the provided test script: `python test_sentry.py`
4. Consult the DevEnviro team for project-specific issues

Last updated: 2025-07-16