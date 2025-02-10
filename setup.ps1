# Check if running with administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    exit 1
}

# Function to check Python version
function Check-PythonVersion {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.11\.*") {
            Write-Host "Python 3.11 is already installed"
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Step 1: Check and Install Python 3.11 if not present
Write-Host "Step 1: Checking Python 3.11 installation..."
if (-not (Check-PythonVersion)) {
    Write-Host "Installing Python 3.11..."
    # Download Python 3.11 installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.0-amd64.exe"
    
    Write-Host "Downloading Python 3.11..."
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    
    Write-Host "Installing Python 3.11..."
    # Install Python with pip and add to PATH
    Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    Remove-Item $installerPath
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "Python 3.11 installation completed"
} else {
    Write-Host "Python 3.11 is already installed"
}

# Step 2: Create virtual environment
Write-Host "Step 2: Creating virtual environment..."
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Recreating it..."
    Remove-Item -Recurse -Force "venv"
}
python -m venv venv

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Verify Python version
$pythonVersion = python --version
Write-Host "Using $pythonVersion in virtual environment"

# Step 4: Install uv inside virtual environment
Write-Host "Step 4: Installing uv in virtual environment..."
python -m pip install --upgrade pip
python -m pip install uv

# Step 5: Install project requirements using uv
Write-Host "Step 5: Installing project requirements..."
uv pip install -r requirements.txt

# Step 6: Check and Install Ollama
Write-Host "Step 6: Checking Ollama installation..."
$ollamaDir = "$env:ProgramFiles\Ollama"
$ollamaExe = "$ollamaDir\ollama.exe"

if (-not (Test-Path $ollamaExe)) {
    Write-Host "Installing Ollama..."
    $ollamaUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows.zip"
    $ollamaZip = "$env:TEMP\ollama-windows.zip"

    # Download and extract Ollama
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaZip
    
    # Create Ollama directory if it doesn't exist
    if (-not (Test-Path $ollamaDir)) {
        New-Item -ItemType Directory -Path $ollamaDir | Out-Null
    }
    
    Expand-Archive -Path $ollamaZip -DestinationPath $ollamaDir -Force
    Remove-Item $ollamaZip

    # Add Ollama to PATH if not already there
    $oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if (-not $oldPath.Contains($ollamaDir)) {
        $newPath = "$oldPath;$ollamaDir"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        $env:Path = $newPath
    }
} else {
    Write-Host "Ollama is already installed"
}

# Check if Ollama service is running
$ollamaProcess = Get-Process "ollama" -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "Starting Ollama service..."
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    # Wait for service to start
    Start-Sleep -Seconds 5
} else {
    Write-Host "Ollama service is already running"
}

# Step 7: Pull Llama model
Write-Host "Step 7: Checking Llama 3.2 model..."
$modelExists = ollama list | Select-String "llama3.2"
if (-not $modelExists) {
    Write-Host "Pulling Llama 3.2 model..."
    ollama pull llama3.2
} else {
    Write-Host "Llama 3.2 model is already downloaded"
}

Write-Host "Setup completed successfully!"
Write-Host "To start using the application:"
Write-Host "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
Write-Host "1. Activate the virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Start the server: uvicorn main:app --reload"
Write-Host "3. Open http://localhost:8000 in your browser" 
