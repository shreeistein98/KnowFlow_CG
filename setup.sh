#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS='Linux';;
    Darwin*)    OS='Mac';;
    *)          echo "This script only supports Linux and macOS. For Windows, please use setup.ps1"; exit 1;;
esac

echo "Detected OS: ${OS}"

# Step 1: Install Homebrew (macOS only)
if [ "$OS" = "Mac" ]; then
    if ! command -v brew &> /dev/null; then
        echo "Step 1: Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Step 1: Homebrew already installed"
    fi
fi

# Step 2: Install Python 3.11
echo "Step 2: Installing Python 3.11..."
if [ "$OS" = "Mac" ]; then
    brew install python@3.11
elif [ "$OS" = "Linux" ]; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3.11 python3.11-venv
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3.11
    else
        echo "Unsupported Linux distribution. Please install Python 3.11 manually."
        exit 1
    fi
fi

# Step 3: Create virtual environment with Python 3.11
echo "Step 3: Creating virtual environment..."
python3.11 -m venv venv

# Step 4: Activate virtual environment
echo "Step 4: Activating virtual environment..."
source venv/bin/activate

# Verify Python version
python_version=$(python --version)
echo "Using $python_version in virtual environment"

# Step 5: Install uv inside virtual environment
echo "Step 5: Installing uv in virtual environment..."
python -m pip install uv

# Step 6: Install project requirements using uv
echo "Step 6: Installing project requirements..."
uv pip install -r requirements.txt

# Step 7: Install Ollama
echo "Step 7: Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    if [ "$OS" = "Mac" ]; then
        brew install ollama
    elif [ "$OS" = "Linux" ]; then
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    echo "Ollama already installed"
fi

# Step 8: Pull Llama model
echo "Step 8: Pulling Llama 3.2 model..."
ollama pull llama3.2

echo "Setup completed successfully!"
echo "To start using the application:"
echo "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the server: uvicorn main:app --reload"
echo "3. Open http://localhost:8000 in your browser" 


