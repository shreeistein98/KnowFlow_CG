# Check if running with administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    exit 1
}

# Step 1: Install Python 3.11 if not present
Write-Host "Step 1: Installing Python 3.11..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    # Download Python 3.11 installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.0-amd64.exe"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    
    # Install Python with pip and add to PATH
    Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    Remove-Item $installerPath
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Python already installed"
}

# Step 2: Create virtual environment
Write-Host "Step 2: Creating virtual environment..."
python -m venv venv

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Verify Python version
$pythonVersion = python --version
Write-Host "Using $pythonVersion in virtual environment"

# Step 4: Install uv inside virtual environment
Write-Host "Step 4: Installing uv in virtual environment..."
python -m pip install uv

# Step 5: Install project requirements using uv
Write-Host "Step 5: Installing project requirements..."
uv pip install -r requirements.txt

# Step 6: Install Ollama
Write-Host "Step 6: Installing Ollama..."
$ollamaUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows.zip"
$ollamaZip = "$env:TEMP\ollama-windows.zip"
$ollamaDir = "$env:ProgramFiles\Ollama"
$ollamaExe = "$ollamaDir\ollama.exe"

# Download and extract Ollama
Write-Host "Downloading Ollama..."
Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaZip

# Create Ollama directory if it doesn't exist
if (-not (Test-Path $ollamaDir)) {
    New-Item -ItemType Directory -Path $ollamaDir | Out-Null
}

Write-Host "Extracting Ollama..."
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
Write-Host "Starting Ollama service (this may take a minute)..."
$ollamaProcess = Get-Process "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "Stopping existing Ollama service..."
    Stop-Process -Name "ollama" -Force
    Start-Sleep -Seconds 2
}

Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden

# Wait for service to be fully ready
Write-Host "Waiting for Ollama service to start..."
$attempts = 6
$ready = $false
for ($i = 1; $i -le $attempts; $i++) {
    Write-Host "Waiting for Ollama service to be ready... (attempt $i/$attempts)"
    Start-Sleep -Seconds 5
    
    try {
        $process = Get-Process "ollama" -ErrorAction SilentlyContinue
        $test = ollama list 2>$null
        if ($process -and $LASTEXITCODE -eq 0) {
            Write-Host "✓ Ollama service is running and responding"
            $ready = $true
            break
        }
    } catch {
        if ($i -eq $attempts) {
            Write-Host "Error: Failed to start Ollama service after 30 seconds"
            Write-Host "Please try running Ollama manually: $ollamaExe serve"
            exit 1
        }
    }
}

if (-not $ready) {
    Write-Host "Error: Failed to start Ollama service"
    exit 1
}

# Step 7: Pull Llama model
Write-Host "Step 7: Pulling Llama 3.2 model (this may take several minutes)..."
try {
    $modelExists = ollama list | Select-String "llama3.2"
    if (-not $modelExists) {
        Write-Host "Downloading Llama 3.2 model..."
        ollama pull llama3.2
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Llama 3.2 model downloaded successfully"
        } else {
            Write-Host "Error: Failed to pull Llama 3.2 model"
            exit 1
        }
    } else {
        Write-Host "✓ Llama 3.2 model is already downloaded"
    }
} catch {
    Write-Host "Error: Failed to pull Llama 3.2 model"
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host "Setup completed successfully!"
Write-Host "To start using the application:"
Write-Host "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
Write-Host "1. Activate the virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Start the server: uvicorn main:app --reload"
Write-Host "3. Open http://localhost:8000 in your browser" 
