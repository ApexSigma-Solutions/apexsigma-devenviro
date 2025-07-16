#!/bin/bash
# Quick SSH tunnel connection script for your laptop

# Configuration
WINDOWS_IP="192.168.68.108"  # Primary IP - update if needed
USERNAME="steyn"

echo "🔗 Connecting to ApexSigma DevEnviro workspace..."
echo "Windows Machine: $WINDOWS_IP"
echo "Services will be available on localhost after connection"

# Core development services tunnel
ssh -L 8000:localhost:8000 \
    -L 6333:localhost:6333 \
    -L 6334:localhost:6334 \
    "$USERNAME@$WINDOWS_IP"

echo "📡 SSH tunnel established!"
echo ""
echo "🔧 Available services on your laptop:"
echo "  Memory Service API: http://localhost:8000"
echo "  Memory Service Docs: http://localhost:8000/docs" 
echo "  Qdrant Vector DB: http://localhost:6333"
echo "  Qdrant Dashboard: http://localhost:6334/dashboard"
echo ""
echo "✅ Ready for remote development!"