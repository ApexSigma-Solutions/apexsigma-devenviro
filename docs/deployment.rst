Deployment Guide
================

This guide covers deploying the ApexSigma DevEnviro project to various environments.

CI/CD Pipeline
--------------

The project uses GitHub Actions for automated deployment:

**Workflow Triggers:**
- Push to ``main`` branch
- Pull requests to ``main`` branch
- Manual workflow dispatch

**Pipeline Stages:**

1. **Testing:** Run tests on Python 3.10 and 3.11
2. **Code Quality:** Check formatting, linting, and security
3. **Build:** Create distribution packages
4. **Documentation:** Build and deploy to GitHub Pages
5. **Deploy:** Deploy to target environments (when configured)

**Pipeline Configuration:**

The pipeline is defined in ``.github/workflows/ci.yml``:

.. code-block:: yaml

   name: CI/CD Pipeline
   
   on:
     push:
       branches: [ master, main, develop ]
     pull_request:
       branches: [ master, main ]

Environment Configuration
--------------------------

**Development Environment:**

.. code-block:: bash

   # Clone repository
   git clone https://github.com/ApexSigma-Solutions/apexsigma-devenviro.git
   cd apexsigma-devenviro
   
   # Setup virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements-dev.txt
   
   # Setup pre-commit hooks
   pre-commit install

**Staging Environment:**

.. code-block:: bash

   # Production-like environment for testing
   pip install -r requirements.txt
   
   # Set environment variables
   export GEMINI_API_KEY="your_staging_gemini_key"
   export LINEAR_API_KEY="your_staging_linear_key"
   export QDRANT_URL="http://staging-qdrant:6333"
   
   # Run application
   python code/main.py

**Production Environment:**

.. code-block:: bash

   # Install production dependencies only
   pip install -r requirements.txt --no-dev
   
   # Set production environment variables
   export ENVIRONMENT="production"
   export GEMINI_API_KEY="your_production_gemini_key"
   export LINEAR_API_KEY="your_production_linear_key"
   export QDRANT_URL="http://production-qdrant:6333"

Docker Deployment
-----------------

**Dockerfile:**

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Copy requirements first for better caching
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY code/ ./code/
   COPY docs/ ./docs/
   
   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD python -c "from code.monitoring import error_tracker; print(error_tracker.health_check())"
   
   EXPOSE 8000
   
   CMD ["python", "-m", "code.main"]

**Docker Compose:**

.. code-block:: yaml

   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - DATABASE_URL=${DATABASE_URL}
       depends_on:
         - qdrant
       
     qdrant:
       image: qdrant/qdrant:latest
       ports:
         - "6333:6333"
       volumes:
         - qdrant_data:/qdrant/storage
   
   volumes:
     qdrant_data:

**Building and Running:**

.. code-block:: bash

   # Build image
   docker build -t apexsigma-devenviro .
   
   # Run with docker-compose
   docker-compose up -d
   
   # View logs
   docker-compose logs -f app

Cloud Deployment
----------------

**AWS Deployment:**

.. code-block:: yaml

   # deploy.yml - Add to .github/workflows/
   - name: Deploy to AWS
     if: github.ref == 'refs/heads/main'
     run: |
       # Configure AWS credentials
       aws configure set aws_access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
       aws configure set aws_secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}
       aws configure set default.region us-east-1
       
       # Deploy to ECS or Lambda
       aws ecs update-service --cluster prod --service apexsigma-devenviro

**Google Cloud Deployment:**

.. code-block:: bash

   # Deploy to Google Cloud Run
   gcloud run deploy apexsigma-devenviro \
     --image gcr.io/PROJECT_ID/apexsigma-devenviro \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated

**Azure Deployment:**

.. code-block:: bash

   # Deploy to Azure Container Instances
   az container create \
     --resource-group myResourceGroup \
     --name apexsigma-devenviro \
     --image apexsigma/devenviro:latest \
     --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY

Environment Variables
---------------------

**Required Variables:**

.. code-block:: bash

   # Core application
   OPENAI_API_KEY=sk-...
   LINEAR_API_KEY=lin_api_...
   
   # Database
   DATABASE_URL=postgresql://user:pass@host:port/db
   
   # Environment
   ENVIRONMENT=production  # development, staging, production
   DEBUG=false
   
   # Monitoring
   SENTRY_DSN=https://...  # Optional error tracking
   LOG_LEVEL=INFO

**Setting in GitHub Actions:**

1. Go to repository Settings → Secrets and variables → Actions
2. Add repository secrets:
   - ``OPENAI_API_KEY``
   - ``LINEAR_API_KEY``
   - ``DATABASE_URL``
   - ``AWS_ACCESS_KEY_ID`` (if using AWS)
   - ``AWS_SECRET_ACCESS_KEY`` (if using AWS)

**Setting in Production:**

.. code-block:: bash

   # Using environment file
   echo "OPENAI_API_KEY=your_key" >> /etc/environment
   
   # Using systemd service
   echo "Environment=OPENAI_API_KEY=your_key" >> /etc/systemd/system/apexsigma.service

Database Setup
--------------

**PostgreSQL Setup:**

.. code-block:: sql

   -- Create database
   CREATE DATABASE apexsigma_devenviro;
   
   -- Create user
   CREATE USER apexsigma WITH PASSWORD 'secure_password';
   
   -- Grant permissions
   GRANT ALL PRIVILEGES ON DATABASE apexsigma_devenviro TO apexsigma;

**Qdrant Setup:**

.. code-block:: bash

   # Using Docker
   docker run -p 6333:6333 qdrant/qdrant:latest
   
   # Or install locally
   curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar xz
   ./qdrant

Monitoring and Logging
----------------------

**Application Monitoring:**

.. code-block:: python

   from code.monitoring import error_tracker
   
   # Custom monitoring setup
   error_tracker.setup_logging()
   
   # Health check endpoint
   @app.route('/health')
   def health_check():
       return error_tracker.health_check()

**Log Aggregation:**

.. code-block:: yaml

   # Using Fluentd or similar
   logging:
     driver: fluentd
     options:
       fluentd-address: logging-server:24224
       tag: apexsigma.devenviro

**Alerting:**

.. code-block:: python

   # Setup alerts for critical errors
   def critical_error_alert(error):
       if error.level == 'CRITICAL':
           send_slack_notification(error)
           send_email_alert(error)

Security Considerations
-----------------------

**Secret Management:**

- Use environment variables for secrets
- Never commit secrets to version control
- Rotate secrets regularly
- Use secret management services (AWS Secrets Manager, Azure Key Vault)

**Network Security:**

.. code-block:: yaml

   # Example network policy
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: apexsigma-netpol
   spec:
     podSelector:
       matchLabels:
         app: apexsigma-devenviro
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: allowed-namespace

**Container Security:**

.. code-block:: dockerfile

   # Use non-root user
   RUN useradd -m -u 1000 appuser
   USER appuser
   
   # Scan for vulnerabilities
   RUN apt-get update && apt-get upgrade -y
   
   # Remove unnecessary packages
   RUN apt-get autoremove -y && apt-get clean

Performance Optimization
-------------------------

**Application Performance:**

.. code-block:: python

   # Enable performance monitoring
   from code.monitoring import error_tracker
   
   @error_tracker.track_performance
   def expensive_operation():
       # Your code here
       pass

**Resource Limits:**

.. code-block:: yaml

   # Kubernetes resource limits
   resources:
     requests:
       memory: "256Mi"
       cpu: "250m"
     limits:
       memory: "512Mi"
       cpu: "500m"

**Caching:**

.. code-block:: python

   # Redis caching
   import redis
   
   cache = redis.Redis(host='redis-server', port=6379, db=0)
   
   def get_cached_result(key):
       result = cache.get(key)
       if result:
           return json.loads(result)
       return None

Rollback Strategy
-----------------

**Database Rollback:**

.. code-block:: bash

   # Database migration rollback
   alembic downgrade -1
   
   # Restore from backup
   pg_restore -d apexsigma_devenviro backup_file.sql

**Application Rollback:**

.. code-block:: bash

   # Docker rollback
   docker service update --rollback apexsigma-devenviro
   
   # Kubernetes rollback
   kubectl rollout undo deployment/apexsigma-devenviro

**Quick Rollback Commands:**

.. code-block:: bash

   # Automated rollback script
   #!/bin/bash
   
   echo "Rolling back to previous version..."
   
   # Stop current version
   docker-compose down
   
   # Switch to previous image
   docker tag apexsigma-devenviro:previous apexsigma-devenviro:latest
   
   # Start previous version
   docker-compose up -d
   
   echo "Rollback complete"

Deployment Checklist
---------------------

**Pre-deployment:**

- [ ] All tests pass in CI/CD
- [ ] Security scan completed
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Monitoring setup verified
- [ ] Backup strategy in place

**Deployment:**

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Monitor application logs
- [ ] Verify all endpoints working
- [ ] Check database connections
- [ ] Validate external integrations

**Post-deployment:**

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all features working
- [ ] Update documentation
- [ ] Notify stakeholders
- [ ] Schedule post-deployment review

**Troubleshooting Common Issues:**

1. **Container won't start:** Check environment variables and port conflicts
2. **Database connection failed:** Verify credentials and network access
3. **API endpoints returning 500:** Check application logs and dependencies
4. **High memory usage:** Monitor for memory leaks and optimize queries
5. **Slow response times:** Check database performance and caching

Remember to always test deployments in a staging environment before production!