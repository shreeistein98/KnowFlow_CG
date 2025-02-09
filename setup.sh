#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS='Linux';;
    Darwin*)    OS='Mac';;
    *)          echo "This script only supports Linux and macOS. For Windows, please use setup.ps1"; exit 1;;
esac

echo "Detected OS: ${OS}"

# Function to check and install Python 3.11
install_python() {
    if ! command -v python3.11 &> /dev/null; then
        echo "Python 3.11 is not installed. Installing..."
        if [ "$OS" = "Mac" ]; then
            if ! command -v brew &> /dev/null; then
                echo "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
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
    fi
}

# Install Python 3.11 if needed
echo "Step 1: Installing Python 3.11..."
install_python

# Install uv globally using pip
echo "Step 2: Installing uv globally..."
python3.11 -m pip install --user uv

# Create virtual environment with Python 3.11
echo "Step 3: Creating virtual environment with Python 3.11..."
python3.11 -m venv venv

# Activate virtual environment
echo "Step 4: Activating virtual environment..."
source venv/bin/activate

# Verify we're using Python 3.11 in the virtual environment
python_version=$(python --version)
echo "Using $python_version in virtual environment"

# Install requirements using uv
echo "Step 5: Installing requirements using uv..."
uv pip install -r requirements.txt

# Install Ollama if not present
install_ollama() {
    if ! command -v ollama &> /dev/null; then
        echo "Installing Ollama..."
        if [ "$OS" = "Mac" ]; then
            brew install ollama
        elif [ "$OS" = "Linux" ]; then
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    fi
}

install_ollama

# Pull Llama model
echo "Pulling Llama 3.2 3B model..."
ollama pull llama3.2

echo "Setup completed successfully!"
echo "To start using the application:"
echo "NOTE: You need to activate the virtual environment in EACH NEW terminal session"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the server: uvicorn main:app --reload"
echo "3. Open http://localhost:8000 in your browser" 


