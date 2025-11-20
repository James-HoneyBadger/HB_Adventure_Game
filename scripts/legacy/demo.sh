#!/bin/bash
# Complete demo of Eamon Adventures system

clear
echo "======================================================================="
echo "               EAMON ADVENTURES - COMPLETE DEMO"
echo "======================================================================="
echo ""
echo "This demo will show you everything the system can do."
echo ""

# Wait for user
read -p "Press Enter to begin the demo..." 

echo ""
echo "======================================================================="
echo "STEP 1: Verify Installation"
echo "======================================================================="
echo ""
./verify_installation.sh

echo ""
read -p "Press Enter to continue..."

echo ""
echo "======================================================================="
echo "STEP 2: List Available Adventures"
echo "======================================================================="
echo ""
./list_adventures.sh

echo ""
read -p "Press Enter to continue..."

echo ""
echo "======================================================================="
echo "STEP 3: Run Engine Test"
echo "======================================================================="
echo ""
python3 test_engine.py

echo ""
read -p "Press Enter to continue..."

echo ""
echo "======================================================================="
echo "STEP 4: Show Project Files"
echo "======================================================================="
echo ""
echo "Documentation files:"
ls -1 *.md
echo ""
echo "Game files:"
ls -1 *.py
echo ""
echo "Scripts:"
ls -1 *.sh
echo ""
echo "Adventures:"
ls -1 adventures/

echo ""
read -p "Press Enter to continue..."

echo ""
echo "======================================================================="
echo "DEMO COMPLETE"
echo "======================================================================="
echo ""
echo "You now have a complete, working Eamon adventure system!"
echo ""
echo "What you can do now:"
echo ""
echo "  1. PLAY GAMES"
echo "     ./play_eamon.sh              - Menu system"
echo "     ./play_adventure.sh beginners_cave.json"
echo ""
echo "  2. CREATE ADVENTURES"
echo "     cp adventures/beginners_cave.json adventures/my_adventure.json"
echo "     nano adventures/my_adventure.json"
echo "     ./play_adventure.sh my_adventure.json"
echo ""
echo "  3. READ DOCUMENTATION"
echo "     cat QUICKSTART.md            - Quick guide"
echo "     cat README.md                - Full manual"
echo "     cat EXAMPLE_GAMEPLAY.md      - See how to play"
echo ""
echo "  4. EXPLORE THE CODE"
echo "     cat acs_engine.py            - Game engine"
echo "     cat acs_launcher.py          - Menu system"
echo "     cat acs_ide.py               - IDE"
echo "     cat adventures/*.json        - Adventure data"
echo ""
echo "======================================================================="
echo ""
echo "Recommended first step: ./play_eamon.sh"
echo ""
