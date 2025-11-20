#!/bin/bash
# Installation and System Check for Eamon Adventures

echo "======================================================================="
echo "          EAMON ADVENTURES - INSTALLATION VERIFICATION"
echo "======================================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
    version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Found Python $version${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Install with: sudo apt install python3  (Ubuntu/Debian)"
    echo "              : sudo dnf install python3  (Fedora)"
    echo "              : sudo pacman -S python     (Arch)"
    exit 1
fi

# Check Python version
echo -n "Checking Python version... "
version_check=$(python3 -c "import sys; print(1 if sys.version_info >= (3,6) else 0)")
if [ "$version_check" = "1" ]; then
    echo -e "${GREEN}✓ Version OK (3.6+)${NC}"
else
    echo -e "${RED}✗ Python 3.6+ required${NC}"
    exit 1
fi

# Check files
echo ""
echo "Checking project files..."

files=(
    "acs_engine.py:Game Engine"
    "acs_launcher.py:Launcher"
    "acs_ide.py:IDE"
    "play_eamon.sh:Play Script"
    "play_adventure.sh:Direct Play Script"
    "list_adventures.sh:List Script"
    "adventures/beginners_cave.json:Beginner's Cave"
    "adventures/lair_of_mutants.json:Lair of Mutants"
)

all_found=true
for item in "${files[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    echo -n "  $desc... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ Missing${NC}"
        all_found=false
    fi
done

if [ "$all_found" = false ]; then
    echo ""
    echo -e "${RED}Some files are missing. Please reinstall.${NC}"
    exit 1
fi

# Check script permissions
echo ""
echo "Checking script permissions..."
scripts=("play_eamon.sh" "play_adventure.sh" "list_adventures.sh")
needs_chmod=false

for script in "${scripts[@]}"; do
    echo -n "  $script... "
    if [ -x "$script" ]; then
        echo -e "${GREEN}✓ Executable${NC}"
    else
        echo -e "${YELLOW}⚠ Not executable${NC}"
        needs_chmod=true
    fi
done

if [ "$needs_chmod" = true ]; then
    echo ""
    echo -e "${YELLOW}Run: chmod +x *.sh${NC}"
    chmod +x *.sh
    echo "Fixed permissions automatically."
fi

# Test engine import
echo ""
echo -n "Testing game engine... "
if python3 -c "import acs_engine" 2>/dev/null; then
    echo -e "${GREEN}✓ Import OK${NC}"
else
    echo -e "${RED}✗ Import failed${NC}"
    exit 1
fi

# Count adventures
echo ""
adventure_count=$(ls -1 adventures/*.json 2>/dev/null | wc -l)
echo "Found $adventure_count adventure(s)"

# Project stats
echo ""
echo "Project Statistics:"
total_lines=$(find . -name "*.py" -o -name "*.json" -o -name "*.sh" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
echo "  Total lines: $total_lines"

python_files=$(find . -name "*.py" | wc -l)
echo "  Python files: $python_files"

echo ""
echo "======================================================================="
echo -e "                    ${GREEN}✓ INSTALLATION VERIFIED${NC}"
echo "======================================================================="
echo ""
echo "Ready to play! Choose one:"
echo ""
echo "  1. Menu system:    ./play_eamon.sh"
echo "  2. Direct play:    ./play_adventure.sh beginners_cave.json"
echo "  3. List games:     ./list_adventures.sh"
echo "  4. Run test:       python3 test_engine.py"
echo ""
echo "Documentation:"
echo "  - README.md          : Complete documentation"
echo "  - QUICKSTART.md      : Quick start guide"
echo "  - EXAMPLE_GAMEPLAY.md: Sample game session"
echo ""
echo "======================================================================="
