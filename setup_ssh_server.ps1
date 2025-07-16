# Install and configure OpenSSH Server on Windows
Write-Host "Setting up SSH Server for remote access..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges. Please run PowerShell as Administrator."
    exit 1
}

# Install OpenSSH Server
Write-Host "Installing OpenSSH Server..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and enable SSH service
Write-Host "Starting SSH service..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Configure firewall
Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue | Select-Object Name, Enabled)) {
    Write-Host "Creating firewall rule for SSH..."
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
} else {
    Write-Host "SSH firewall rule already exists"
}

# Get current IP address
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1"} | Select-Object -First 1).IPAddress
Write-Host "Machine IP Address: $ip" -ForegroundColor Green

# Show current user for SSH access
$currentUser = $env:USERNAME
Write-Host "SSH Access: ssh $currentUser@$ip" -ForegroundColor Green

Write-Host "SSH Server setup complete!" -ForegroundColor Green
Write-Host "You can now connect from your laptop using:" -ForegroundColor Cyan
Write-Host "ssh $currentUser@$ip" -ForegroundColor White