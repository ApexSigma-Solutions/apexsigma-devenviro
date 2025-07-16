# SSH Tunnel Setup for Remote Development Access

## Overview
This guide sets up SSH tunneling to access the ApexSigma DevEnviro workspace remotely from your laptop at work.

## Current Services Running
- **Memory Service**: Port 8000 (Simple Memory API)
- **Qdrant Vector DB**: Port 6333 (Vector database)
- **Qdrant Web UI**: Port 6334 (Optional web interface)
- **PostgreSQL**: Port 5432 (Database)
- **Grafana**: Port 39872 (Monitoring)
- **Prometheus**: Port 39871 (Metrics)

## Step 1: Install SSH Server (Run as Administrator)
```powershell
# Run this PowerShell script as Administrator
.\setup_ssh_server.ps1
```

## Step 2: SSH Tunnel Commands (From Your Laptop)

### Basic SSH Connection
```bash
ssh steyn@<WINDOWS_MACHINE_IP>
```

### Forward All Development Services
```bash
ssh -L 8000:localhost:8000 \
    -L 6333:localhost:6333 \
    -L 6334:localhost:6334 \
    -L 5432:localhost:5432 \
    -L 39872:localhost:39872 \
    -L 39871:localhost:39871 \
    steyn@<WINDOWS_MACHINE_IP>
```

### Simplified Development Tunnel (Core Services Only)
```bash
ssh -L 8000:localhost:8000 -L 6333:localhost:6333 steyn@<WINDOWS_MACHINE_IP>
```

## Step 3: Access Services from Your Laptop

After establishing the tunnel, access services locally:

- **Memory Service API**: http://localhost:8000
- **Memory Service Docs**: http://localhost:8000/docs
- **Qdrant Vector DB**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6334/dashboard

## Step 4: Test Remote Development

### Test Memory Service
```bash
curl http://localhost:8000/health
curl http://localhost:8000/memory/stats
```

### Test Qdrant
```bash
curl http://localhost:6333/collections
```

## Step 5: Development Workflow

1. **Connect via SSH tunnel** (forward ports 8000, 6333)
2. **Run your code** on the Windows machine via SSH
3. **Access services** through localhost on your laptop
4. **Use local browser** to interact with APIs and dashboards

## Security Notes

- SSH keys recommended for authentication
- Consider VPN instead of direct SSH if on corporate network
- Firewall rules created for port 22 only
- Services remain bound to localhost for security

## Troubleshooting

### If SSH connection fails:
- Check Windows Firewall settings
- Verify SSH service is running: `Get-Service sshd`
- Check network connectivity: `ping <WINDOWS_MACHINE_IP>`

### If port forwarding fails:
- Ensure services are running on Windows machine
- Check for port conflicts on laptop
- Verify tunnel command syntax

## Advanced: Background Tunnel
To keep tunnel running in background:
```bash
ssh -fN -L 8000:localhost:8000 -L 6333:localhost:6333 steyn@<WINDOWS_MACHINE_IP>
```