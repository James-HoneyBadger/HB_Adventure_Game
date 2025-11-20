# Adventure Construction Set - File Organization

## Overview

The project has been reorganized into a clean, professional structure following Python best practices.

## Directory Structure

```
HB_Eamon/
├── src/acs/              # Main source code (Python package)
│   ├── __init__.py
│   ├── core/            # Core game engine
│   │   ├── __init__.py
│   │   ├── engine.py           # Main game engine
│   │   ├── engine_enhanced.py  # Enhanced features
│   │   ├── parser.py           # Natural language parser
│   │   ├── game_state.py       # Game state management
│   │   ├── event_bus.py        # Event system
│   │   ├── services.py         # Core services
│   │   └── base_plugin.py      # Plugin base class
│   │
│   ├── systems/         # Game systems
│   │   ├── __init__.py
│   │   ├── combat.py           # Combat system
│   │   ├── npc_context.py      # NPC AI and context
│   │   ├── environment.py      # Environmental effects
│   │   ├── achievements.py     # Achievement tracking
│   │   ├── journal.py          # Quest journal
│   │   └── tutorial.py         # Tutorial system
│   │
│   ├── ui/              # User interfaces
│   │   ├── __init__.py
│   │   ├── ide.py              # Graphical IDE
│   │   ├── launcher.py         # Game launcher
│   │   └── accessibility.py    # Accessibility features
│   │
│   ├── tools/           # Utility tools
│   │   ├── __init__.py
│   │   ├── dsk_converter.py    # Eamon DSK file converter
│   │   ├── commands.py         # Smart command system
│   │   └── modding.py          # Modding support
│   │
│   └── data/            # Data management
│       ├── __init__.py
│       ├── config_service.py   # Configuration
│       ├── data_service.py     # Data loading/saving
│       └── io_service.py       # I/O operations
│
├── scripts/             # Executable launcher scripts
│   ├── acs-ide                 # Launch IDE
│   ├── acs-play                # Play adventures
│   ├── acs-convert             # Convert DSK files
│   └── legacy/                 # Old bin/ scripts (deprecated)
│
├── adventures/          # Adventure JSON files
├── config/              # Configuration files
├── docs/                # Documentation
├── tests/               # Test files
├── examples/            # Example adventures
│
├── archive/             # Archived content
│   ├── Original_Games/         # Original Eamon games
│   └── test_adventure.dsk      # Test file
│
├── quickstart.sh        # Quick start menu
├── README.md            # Main documentation
├── LICENSE              # MIT License
└── .gitignore           # Git ignore rules
```

## Import Changes

All imports have been updated to use the new package structure:

### Old Style (deprecated)
```python
from acs_engine import GameEngine
from acs_parser import NaturalLanguageParser
```

### New Style (current)
```python
from acs.core.engine import GameEngine
from acs.core.parser import NaturalLanguageParser
```

## Running the Application

### Using Scripts (Recommended)
```bash
./quickstart.sh           # Interactive menu
./scripts/acs-ide         # Launch IDE
./scripts/acs-play        # Play adventures
./scripts/acs-convert     # Convert DSK files
```

### Using Python Directly
```bash
python3 -m acs.ui.ide
python3 -m acs.ui.launcher
```

## Benefits of New Structure

1. **Professional Organization** - Follows Python packaging standards
2. **Clear Separation** - Core, systems, UI, and tools are separated
3. **Easy Imports** - Logical import paths (acs.core.engine)
4. **Scalability** - Easy to add new modules
5. **Testing** - Clear structure for test organization
6. **Distribution** - Ready for pip installation if needed

## Migration Notes

- All old root-level `acs_*.py` files have been moved to `src/acs/`
- Old `core/`, `systems/`, and `utils/` directories have been consolidated
- Shell scripts moved from `bin/` to `scripts/`
- Archive content moved to `archive/`
- All imports updated to new package paths

## Next Steps

To make this an installable package, create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="adventure-construction-set",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "acs-ide=acs.ui.ide:main",
            "acs-play=acs.ui.launcher:main",
            "acs-convert=acs.tools.dsk_converter:main",
        ],
    },
)
```

Then install with: `pip install -e .`
