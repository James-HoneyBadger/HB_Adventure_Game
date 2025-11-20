#!/bin/bash
# Adventure Construction Set Launcher Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 to play adventures."
    exit 1
fi

# Run the launcher
cd "$SCRIPT_DIR"
python3 acs_launcher.py "$@"
