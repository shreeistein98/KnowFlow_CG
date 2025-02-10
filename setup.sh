#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS='Linux';;
    Darwin*)    OS='Mac';;
    *)          echo "This script only supports Linux and macOS. For Windows, please use setup.ps1"; exit 1;;
esac

echo "Detected OS: ${OS}"

# Function to check Python version
check_python_version() {
    if command -v python3.11 &> /dev/null; then
        echo "Python 3.11 is already installed"
        return 0
    fi
    return 1
}

# Step 1: Install Homebrew (macOS only)
if [ "$OS" = "Mac" ]; then
    echo "Step 1: Checking Homebrew installation..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        # Add Homebrew to PATH if needed
        if [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo "Homebrew is already installed"
    fi
fi

# Step 2: Install Python 3.11
echo "Step 2: Checking Python 3.11 installation..."
if ! check_python_version; then
    echo "Installing Python 3.11..."
    if [ "$OS" = "Mac" ]; then
        brew install python@3.11
    elif [ "$OS" = "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3.11 python3.11-devel
        else
            echo "Unsupported Linux distribution. Please install Python 3.11 manually."
            exit 1
        fi
    fi
fi

# Step 3: Create virtual environment with Python 3.11
echo "Step 3: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Recreating it..."
    rm -rf venv
fi
python3.11 -m venv venv

# Step 4: Activate virtual environment
echo "Step 4: Activating virtual environment..."
source venv/bin/activate

# Verify Python version
python_version=$(python --version)
echo "Using $python_version in virtual environment"

# Step 5: Install uv inside virtual environment
echo "Step 5: Installing uv in virtual environment..."
python -m pip install --upgrade pip
python -m pip install uv

# Step 6: Install project requirements using uv
echo "Step 6: Installing project requirements..."
uv pip install -r requirements.txt

# Step 7: Install Ollama
echo "Step 7: Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    if [ "$OS" = "Mac" ]; then
        brew install ollama
    elif [ "$OS" = "Linux" ]; then
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    echo "Ollama is already installed"
fi

# Start Ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    if [ "$OS" = "Mac" ]; then
        brew services start ollama
    else
        sudo systemctl start ollama
    fi
    # Wait for service to start
    sleep 5
fi

# Step 8: Pull Llama model
echo "Step 8: Pulling Llama 3.2 model..."
if ! ollama list | grep -q "llama3.2"; then
    ollama pull llama3.2
else
    echo "Llama 3.2 model is already downloaded"
fi

echo "Setup completed successfully!"
echo "To start using the application:"
echo "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the server: uvicorn main:app --reload"
echo "3. Open http://localhost:8000 in your browser" 


