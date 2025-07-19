#!/bin/bash
# DevEnviro Enhanced Startup Script
# Quick launcher for cognitive collaboration workspace

echo "DevEnviro Enhanced Startup"
echo "=========================="

# Change to script directory
cd "$(dirname "$0")"

# Run the Python startup script
python3 devenviro_startup.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Press Enter to continue..."
    read
fi