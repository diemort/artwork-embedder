#!/bin/bash

# Define environment name
ENV_NAME="mp3tagger-env"
APIKEY="${APIKEY:-}"

# Use existing APIKEY or prompt the user
if [ -z "$APIKEY" ]; then
    read -p "🔑 Enter your AcoustID API key (press Enter to skip): " APIKEY
    if [ -z "$APIKEY" ]; then
        echo "⚠️  No API key provided. AcoustID fallback will be disabled."
        echo "    You can add your key later to the .env file:"
        echo "    ACOUSTID_API_KEY=\"your-key-here\""
    else
        echo "🔐 API key entered."
        echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
        echo "✅ API key saved to .env"
    fi
else
    echo "🔐 Using provided API key."
    echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
    echo "✅ API key saved to .env"
fi

echo ""
echo "🔧 Setting up environment: $ENV_NAME"

# Detect OS
OS_TYPE=$(uname)
case "$OS_TYPE" in
    Darwin)
        PLATFORM="macOS"
        ;;
    Linux)
        if grep -qi microsoft /proc/version; then
            PLATFORM="WSL"
        else
            PLATFORM="Linux"
        fi
        ;;
    *)
        echo "❌ Unsupported OS: $OS_TYPE"
        exit 1
        ;;
esac

echo "🖥️ Detected platform: $PLATFORM"

# Install chromaprint (fpcalc) based on platform
if ! command -v fpcalc &> /dev/null; then
    echo "📦 Installing chromaprint (fpcalc)..."
    case "$PLATFORM" in
        macOS)
            if ! command -v brew &> /dev/null; then
                echo "❌ Homebrew not found. Please install it: https://brew.sh"
                exit 1
            fi
            brew install chromaprint
            ;;
        Linux|WSL)
            sudo apt update
            sudo apt install -y chromaprint
            ;;
    esac
else
    echo "✅ chromaprint already installed."
fi

# Create virtual environment if not exists
if [ ! -d "$ENV_NAME" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv "$ENV_NAME"
else
    echo "✅ Virtual environment already exists."
fi

# Activate environment
source "$ENV_NAME/bin/activate"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing pip modules..."
pip install pyacoustid mutagen requests music-tag tinytag python-dotenv musicbrainzngs requests

# Save API key to .env
echo "ACOUSTID_API_KEY=\"$APIKEY\"" > .env
echo "✅ API key saved to .env"

echo ""
echo "🎉 Setup complete!"
echo "➡️ To activate the environment later, run: source $ENV_NAME/bin/activate"

