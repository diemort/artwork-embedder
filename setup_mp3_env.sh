#!/bin/bash

# Define environment name and pause-on-error helper
ENV_NAME="mp3tagger-env"
APIKEY="${APIKEY:-}"

pause_exit() {
    echo ""
    read -p "Press Enter to exit..."
    exit 1
}

# Prompt for AcoustID API key
if [ -z "$APIKEY" ]; then
    read -p "Enter your AcoustID API key (press Enter to skip): " APIKEY
    if [ -z "$APIKEY" ]; then
        echo "No API key provided. AcoustID fallback will be disabled."
        echo "You can add it later to the .env file like this:"
        echo 'ACOUSTID_API_KEY="your-key-here"'
    fi
fi

# Save API key to .env
echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
echo "Saved API key to .env"

echo ""
echo "Setting up environment: $ENV_NAME"

# Detect platform
OS_TYPE=$(uname)
case "$OS_TYPE" in
    Darwin)
        PLATFORM="macOS"
        ;;
    Linux)
        if grep -qi microsoft /proc/version 2>/dev/null; then
            PLATFORM="WSL"
        else
            PLATFORM="Linux"
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="Windows"
        ;;
    *)
        echo "Unsupported OS: $OS_TYPE"
        pause_exit
        ;;
esac

echo "Detected platform: $PLATFORM"

# Check for Python 3.12
if command -v python3.12 &> /dev/null; then
    PYTHON_BIN=$(command -v python3.12)
else
    echo "Python 3.12 is not installed."
    case "$PLATFORM" in
        macOS)
            echo "Install with: brew install python@3.12"
            ;;
        Linux|WSL)
            echo "Install with: sudo apt install python3.12"
            ;;
        Windows)
            echo "Download from: https://www.python.org/downloads/windows/"
            ;;
    esac
    pause_exit
fi

PY_VERSION=$($PYTHON_BIN -V)
echo "Using $PY_VERSION"

# Check for chromaprint (fpcalc)
if ! command -v fpcalc &> /dev/null; then
    echo "Installing chromaprint (fpcalc)..."
    case "$PLATFORM" in
        macOS)
            if ! command -v brew &> /dev/null; then
                echo "Homebrew not found. Please install it from https://brew.sh"
                pause_exit
            fi
            brew install chromaprint
            ;;
        Linux|WSL)
            sudo apt update && sudo apt install -y chromaprint
            ;;
        Windows)
            echo "Please install Chromaprint manually:"
            echo "https://acoustid.org/chromaprint"
            pause_exit
            ;;
    esac
else
    echo "chromaprint (fpcalc) already installed."
fi

# Create virtual environment
if [ ! -d "$ENV_NAME" ]; then
    echo "Creating Python 3.12 virtual environment..."
    "$PYTHON_BIN" -m venv "$ENV_NAME"
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
if [ -f "$ENV_NAME/bin/activate" ]; then
    source "$ENV_NAME/bin/activate"
else
    echo "Could not activate the virtual environment."
    pause_exit
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Check for requirements.txt
if [ ! -f requirements.txt ]; then
    echo "Missing requirements.txt file."
    pause_exit
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete."
echo "To activate the environment later, run:"
echo "source \"$ENV_NAME/bin/activate\""