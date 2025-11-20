#!/bin/bash
# List all available Eamon adventures with details

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADVENTURES_DIR="$SCRIPT_DIR/adventures"

echo "======================================================================="
echo "                     AVAILABLE EAMON ADVENTURES"
echo "======================================================================="
echo ""

if [ ! -d "$ADVENTURES_DIR" ]; then
    echo "No adventures directory found!"
    exit 1
fi

count=0
for adventure in "$ADVENTURES_DIR"/*.json; do
    if [ -f "$adventure" ]; then
        count=$((count + 1))
        filename=$(basename "$adventure")
        
        # Extract title and author using Python
        title=$(python3 -c "import json; f=open('$adventure'); d=json.load(f); print(d.get('title', 'Untitled')); f.close()" 2>/dev/null)
        author=$(python3 -c "import json; f=open('$adventure'); d=json.load(f); print(d.get('author', 'Unknown')); f.close()" 2>/dev/null)
        
        echo "$count. $title"
        echo "   by $author"
        echo "   File: $filename"
        echo ""
    fi
done

if [ $count -eq 0 ]; then
    echo "No adventures found!"
    echo "Add .json files to: $ADVENTURES_DIR"
else
    echo "Total: $count adventure(s)"
    echo ""
    echo "To play: ./play_adventure.sh <filename>"
    echo "   or:   ./play_eamon.sh"
fi

echo "======================================================================="
