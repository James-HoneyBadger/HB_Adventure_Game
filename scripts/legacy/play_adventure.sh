#!/bin/bash
# Quick play script - launches a specific adventure directly

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <adventure_name.json>"
    echo "Example: $0 beginners_cave.json"
    echo ""
    echo "Available adventures:"
    ls -1 "$SCRIPT_DIR/adventures/"*.json 2>/dev/null | xargs -n1 basename
    exit 1
fi

ADVENTURE="$1"

# Check if path is relative or absolute
if [[ ! "$ADVENTURE" = /* ]]; then
    # Relative path - check in adventures directory
    if [ ! -f "$SCRIPT_DIR/adventures/$ADVENTURE" ]; then
        echo "Error: Adventure '$ADVENTURE' not found in adventures directory"
        exit 1
    fi
    ADVENTURE="$SCRIPT_DIR/adventures/$ADVENTURE"
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Run the game
cd "$SCRIPT_DIR"
python3 acs_engine.py "$ADVENTURE"
