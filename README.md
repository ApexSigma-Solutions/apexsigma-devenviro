# ApexSigma DevEnviro Project

Building a cognitive collaboration system on Windows with WSL2, featuring comprehensive error tracking and monitoring with Sentry integration.

## Environment
- OS: Windows with WSL2 Debian
- Python 3.9+ with modern tooling
- Docker services for memory and vector storage
- FastAPI web framework with Sentry error tracking
- Comprehensive monitoring and logging system

## Current Status
- ✅ Basic project structure with packaging
- ✅ FastAPI application with Sentry integration (port 8001)
- ✅ Memory service (simple SQLite-based) running on port 8000
- ✅ Qdrant vector database running on port 6333
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Security scanning and code quality tools
- ✅ OpenRouter API integration support
- ✅ Comprehensive error tracking and monitoring
- ✅ Docker deployment configuration
- ✅ Environment-specific configuration management

## Services
- **DevEnviro API**: http://localhost:8001 (FastAPI with Sentry)
- **Memory Service**: http://localhost:8000 (24 memories, 6 users)
- **Qdrant Vector DB**: http://localhost:6333 (6 collections)
- **Sentry Monitoring**: Real-time error tracking and performance monitoring

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn devenviro.main:app --host 0.0.0.0 --port 8001 --reload

# Test Sentry integration
python test_sentry.py
```

### Docker Deployment
```bash
# Start the complete stack
docker-compose up -d

# Check service health
curl http://localhost:8000/health  # DevEnviro API
curl http://localhost:6333/health  # Qdrant
```

### Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Set required variables:
   ```env
   ENVIRONMENT=development
   SENTRY_DSN=your-sentry-dsn
   OPENROUTER_API_KEY=your-openrouter-key
   ```

## API Endpoints

### Health & Status
- `GET /health` - Application health check
- `GET /system/status` - System monitoring information

### Memory Operations
- `POST /memories` - Create new memory
- `GET /memories/{user_id}` - Get user memories

### Testing & Debug
- `POST /test-error` - Test Sentry error capture
- `GET /sentry-debug` - Trigger test exception

## Architecture

### Core Components
- **devenviro/main.py** - FastAPI application with Sentry integration
- **devenviro/sentry_config.py** - Sentry configuration and utilities
- **devenviro/monitoring.py** - Error tracking and performance monitoring
- **docker-compose.yml** - Production deployment configuration

### Error Tracking
- **Automatic Exception Capture** - All unhandled exceptions sent to Sentry
- **Performance Monitoring** - API endpoint response time tracking
- **User Context** - User information attached to error reports
- **Custom Metrics** - Application-specific monitoring

## Documentation

- **[Sentry Integration Guide](SENTRY_INTEGRATION.md)** - Complete setup and usage
- **[Security Documentation](SECURITY.md)** - Security practices and scanning
- **[API Documentation](docs/)** - Generated API documentation

## Development Tools

### Code Quality
```bash
# Linting
python -m flake8 devenviro/ --max-line-length=127

# Type checking
python -m mypy devenviro/ --ignore-missing-imports

# Testing
python -m pytest tests/
```

### Monitoring
- **Sentry Dashboard**: https://sentry.io/organizations/apexsigma/
- **Local Logs**: `logs/` directory
- **Performance Metrics**: `logs/performance.jsonl`

## Next Steps
- Expand AI-powered memory operations with OpenRouter integration
- Implement advanced cognitive collaboration features
- Add user authentication and authorization
- Enhance vector search capabilities with Qdrant
- Implement real-time collaboration features
