#!/bin/bash
# Launch the Adventure Construction Set IDE

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================================="
echo "           ADVENTURE CONSTRUCTION SET - GRAPHICAL EDITOR"
echo "======================================================================="
echo ""

# Check Python and tkinter
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "Error: Python tkinter is required but not installed."
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch: sudo pacman -S tk"
    exit 1
fi

# Launch IDE
cd "$SCRIPT_DIR"
python3 acs_ide.py

exit $?
