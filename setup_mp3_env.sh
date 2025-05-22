#!/bin/bash

# setup_mp3_env.sh
# Sets up the virtual environment and installs requirements for the artwork-embedder Python module

ENV_NAME="mp3tagger-env"
PYTHON_REQUIRED="3.12"
REQUIREMENTS_FILE="requirements.txt"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" != "$PYTHON_REQUIRED" ]]; then
    echo "❌ Python $PYTHON_REQUIRED is required. Found Python $PYTHON_VERSION."
    echo "Please install Python $PYTHON_REQUIRED and try again."
    exit 1
fi

# Prompt for AcoustID API key
APIKEY="${APIKEY:-}"
if [ -z "$APIKEY" ]; then
    read -p "Enter your AcoustID API key (or press Enter to skip): " APIKEY
    if [ -z "$APIKEY" ]; then
        echo "No API key entered. You can manually edit .env later."
    else
        echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
        echo "API key saved to .env"
    fi
else
    echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
    echo "API key saved to .env"
fi

# Detect OS and install fpcalc if not available
if ! command -v fpcalc &> /dev/null; then
    OS_TYPE=$(uname)
    case "$OS_TYPE" in
        Darwin)
            echo "Installing Chromaprint via Homebrew..."
            if ! command -v brew &> /dev/null; then
                echo "Homebrew not found. Please install it: https://brew.sh"
                exit 1
            fi
            brew install chromaprint
            ;;
        Linux)
            echo "Installing Chromaprint via APT..."
            sudo apt update && sudo apt install -y chromaprint
            ;;
        *)
            echo "Unsupported OS: $OS_TYPE"
            exit 1
            ;;
    esac
else
    echo "Chromaprint (fpcalc) is already installed."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$ENV_NAME" ]; then
    echo "Creating virtual environment: $ENV_NAME"
    python3 -m venv "$ENV_NAME"
fi

# Activate the virtual environment
source "$ENV_NAME/bin/activate"

# Upgrade pip and install dependencies
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# Done
echo "Setup complete. To activate your environment later, run:"
echo "source $ENV_NAME/bin/activate"

