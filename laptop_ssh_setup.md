# SSH Key Setup for Your Work Laptop

## Step 1: Save Private Key on Your Laptop

Create the SSH directory and save the private key:

```bash
# Create SSH directory
mkdir -p ~/.ssh

# Save this private key as ~/.ssh/apexsigma_key
cat > ~/.ssh/apexsigma_key << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCx3gsENOWiph2LnbRUfpR/waFzm/c+nFW+559wE7umBQAAAKirv2w4q79s
OAAAAAtzc2gtZWQyNTUxOQAAACCx3gsENOWiph2LnbRUfpR/waFzm/c+nFW+559wE7umBQ
AAAEBn0kGh6mJ+UYLyOkSh4n0wBWOPF5FhoeFU7moC2Y2vorHeCwQ05aKmHYudtFR+lH/B
oXOb9z6cVb7nn3ATu6YFAAAAIWFwZXhzaWdtYS1kZXZlbnZpcm8tcmVtb3RlLWFjY2Vzcw
ECAwQ=
-----END OPENSSH PRIVATE KEY-----
EOF

# Set proper permissions
chmod 600 ~/.ssh/apexsigma_key
chmod 700 ~/.ssh
```

## Step 2: Connect Using SSH Key

### Quick Connection
```bash
ssh -i ~/.ssh/apexsigma_key steyn@192.168.68.108
```

### With Port Forwarding (Development Services)
```bash
ssh -i ~/.ssh/apexsigma_key \
    -L 8000:localhost:8000 \
    -L 6333:localhost:6333 \
    -L 6334:localhost:6334 \
    steyn@192.168.68.108
```

## Step 3: Create SSH Config (Optional but Recommended)

Add to `~/.ssh/config`:
```
Host apexsigma-dev
    HostName 192.168.68.108
    User steyn
    IdentityFile ~/.ssh/apexsigma_key
    LocalForward 8000 localhost:8000
    LocalForward 6333 localhost:6333
    LocalForward 6334 localhost:6334
```

Then connect simply with:
```bash
ssh apexsigma-dev
```

## Step 4: Test Connection

After connecting, test the services:
```bash
# Test memory service
curl http://localhost:8000/health

# Test vector database
curl http://localhost:6333/collections
```

## Background Connection

To keep the tunnel running in background:
```bash
ssh -i ~/.ssh/apexsigma_key -fN \
    -L 8000:localhost:8000 \
    -L 6333:localhost:6333 \
    steyn@192.168.68.108
```

## Troubleshooting

If connection fails:
1. Check network connectivity: `ping 192.168.68.108`
2. Verify SSH server is running on Windows machine
3. Check firewall settings on both machines
4. Ensure private key permissions are correct: `ls -la ~/.ssh/apexsigma_key`

## Security Notes

- Private key is unique to this setup
- Key has no passphrase for convenience
- Consider using SSH agent for better security
- Private key should never be shared or committed to version control