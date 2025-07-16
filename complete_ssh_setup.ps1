# Complete SSH setup with key authentication
Write-Host "Completing SSH setup for passwordless authentication..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges. Please run PowerShell as Administrator."
    exit 1
}

# Install OpenSSH Server if not already installed
Write-Host "Installing OpenSSH Server..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and enable SSH service
Write-Host "Starting SSH service..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Configure firewall
Write-Host "Configuring Windows Firewall..." -ForegroundColor Yellow
if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue | Select-Object Name, Enabled)) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
} else {
    Write-Host "SSH firewall rule already exists"
}

# Configure SSH for key authentication
$sshd_config = "C:\ProgramData\ssh\sshd_config"
Write-Host "Configuring SSH server for key authentication..." -ForegroundColor Yellow

# Backup original config
if (Test-Path $sshd_config) {
    Copy-Item $sshd_config "$sshd_config.backup" -Force
}

# Enable key authentication
$config_content = @"
# SSH Server Configuration for ApexSigma DevEnviro
Port 22
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM no
Subsystem sftp sftp-server.exe
"@

$config_content | Out-File -FilePath $sshd_config -Encoding UTF8 -Force

# Restart SSH service to apply changes
Write-Host "Restarting SSH service..." -ForegroundColor Yellow
Restart-Service sshd

# Get IP address
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1" -and $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -notlike "172.*"} | Select-Object -First 1).IPAddress
$currentUser = $env:USERNAME

Write-Host ""
Write-Host "SSH Setup Complete!" -ForegroundColor Green
Write-Host "Machine IP: $ip" -ForegroundColor Cyan
Write-Host "SSH Access: ssh $currentUser@$ip" -ForegroundColor Cyan
Write-Host ""
Write-Host "Key authentication is configured!" -ForegroundColor Green
Write-Host "Use the private key from laptop_ssh_setup.md on your work laptop" -ForegroundColor Yellow