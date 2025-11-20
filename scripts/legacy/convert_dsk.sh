#!/bin/bash
# Convert Eamon .DSK disk images to JSON format

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================================="
echo "           EAMON DSK TO JSON CONVERTER"
echo "======================================================================="
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: $0 <disk_image.dsk> [output_name.json]"
    echo ""
    echo "Examples:"
    echo "  $0 adventure.dsk"
    echo "  $0 cave_of_mind.dsk cave_of_mind.json"
    echo ""
    echo "This converts Apple II Eamon disk images to JSON format"
    echo "compatible with the Linux Eamon game engine."
    echo ""
    echo "Supported disk formats:"
    echo "  - .dsk (DOS 3.3 disk image)"
    echo "  - .do  (DOS-ordered disk image)"
    echo ""
    exit 1
fi

DSK_FILE="$1"
OUTPUT_FILE="$2"

# Check if file exists
if [ ! -f "$DSK_FILE" ]; then
    echo "Error: File '$DSK_FILE' not found"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Run converter
cd "$SCRIPT_DIR"

if [ -n "$OUTPUT_FILE" ]; then
    python3 dsk_converter.py "$DSK_FILE" "$OUTPUT_FILE"
else
    python3 dsk_converter.py "$DSK_FILE"
fi

exit $?
