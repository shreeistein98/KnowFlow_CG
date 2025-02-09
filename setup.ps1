# Check if running with administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    exit 1
}

# Function to install Python if not present
function Install-Python {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Step 1: Installing Python 3.11..."
        # Download Python 3.11 installer
        $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
        $installerPath = "$env:TEMP\python-3.11.0-amd64.exe"
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
        
        # Install Python
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        Remove-Item $installerPath
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "Python 3.11 is already installed"
    }
}

# Step 1: Install Python 3.11 if needed
Install-Python

# Step 2: Install uv globally
Write-Host "Step 2: Installing uv globally..."
python -m pip install --user uv

# Step 3: Create virtual environment
Write-Host "Step 3: Creating virtual environment with Python 3.11..."
python -m venv venv

# Step 4: Activate virtual environment
Write-Host "Step 4: Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Verify Python version
$pythonVersion = python --version
Write-Host "Using $pythonVersion in virtual environment"

# Step 5: Install requirements using uv
Write-Host "Step 5: Installing requirements using uv..."
uv pip install -r requirements.txt

# Install Ollama
Write-Host "Installing Ollama..."
$ollamaUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows.zip"
$ollamaZip = "$env:TEMP\ollama-windows.zip"
$ollamaDir = "$env:ProgramFiles\Ollama"

# Download and extract Ollama
Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaZip
Expand-Archive -Path $ollamaZip -DestinationPath $ollamaDir -Force
Remove-Item $ollamaZip

# Add Ollama to PATH
$oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $oldPath.Contains($ollamaDir)) {
    $newPath = "$oldPath;$ollamaDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    $env:Path = $newPath
}

# Start Ollama service
Start-Process -FilePath "$ollamaDir\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden

# Wait for Ollama service to start
Start-Sleep -Seconds 5

# Pull Llama model
Write-Host "Pulling Llama 3.2 3B model..."
ollama pull llama3.2

Write-Host "Setup completed successfully!"
Write-Host "To start using the application:"
Write-Host "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
Write-Host "1. Activate the virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Start the server: uvicorn main:app --reload"
Write-Host "3. Open http://localhost:8000 in your browser" 