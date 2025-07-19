#!/bin/bash
# DevEnviro Session Signoff (Linux/WSL)
# Quick launcher for session closing protocol

echo "DevEnviro Session Signoff"
echo "========================"

# Change to script directory
cd "$(dirname "$0")"

# Run the Python signoff script
python3 session_signoff.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Press Enter to continue..."
    read
fi