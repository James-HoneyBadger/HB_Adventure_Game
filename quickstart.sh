#!/usr/bin/env bash
# Quick start script for Adventure Construction Set

cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ADVENTURE CONSTRUCTION SET                        ║
║         Quick Start                                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

What would you like to do?

1. Launch IDE (create/edit adventures)
2. Play an adventure
3. Convert Eamon DSK file
4. Run tests
5. View documentation

EOF

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "Launching IDE..."
        python3 scripts/acs-ide
        ;;
    2)
        echo "Launching adventure player..."
        python3 scripts/acs-play
        ;;
    3)
        echo "DSK Converter"
        python3 scripts/acs-convert
        ;;
    4)
        echo "Running tests..."
        python3 -m pytest tests/ -v
        ;;
    5)
        echo "Documentation is in docs/"
        echo "Start with: docs/QUICKSTART.md"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
