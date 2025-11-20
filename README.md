# Adventure Construction Set

**Modern text adventure creation and gameplay system**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Version 2.0](https://img.shields.io/badge/version-2.0-green.svg)](docs/CHANGELOG.md)

---

## 🎮 What is This?

A powerful **Adventure Construction Set** for creating and playing text adventures with:

- ✨ **Graphical IDE** - Create adventures without coding
- 🧠 **Natural Language Parser** - Understands conversational commands (99.2% accuracy)
- 🎨 **5 Beautiful Themes** - Dark, Light, Dracula, Nord, Monokai
- ⚔️ **Rich Gameplay** - Combat, NPCs, quests, environmental effects
- 🔌 **Plugin System** - Extend with custom features
- 📚 **Comprehensive Docs** - User manual, technical reference, tutorials

## 🚀 Quick Start

```bash
# Clone or download this repository
cd HB_Eamon

# Run the quick start menu
./quickstart.sh

# Or launch directly:
./scripts/acs-ide        # Open IDE
./scripts/acs-play       # Play adventures
./scripts/acs-convert    # Convert Eamon DSK files
```

That's it! No installation needed (Python 3.6+ required).

## 📖 Features

### For Players

- **Classic Text Adventures** with modern enhancements
- **Natural Language Commands** - "what am I carrying?" just works
- **Rich Combat System** - Tactical fights with weapons and armor
- **NPC Interactions** - Talk, trade, recruit party members
- **Quest System** - Track objectives and earn rewards
- **Save/Load** - Never lose progress

### For Creators

- **Visual IDE** - No programming required
- **Room Editor** - Design locations with exits and descriptions
- **Item Creator** - Weapons, armor, treasures, quest items
- **NPC Designer** - Configure personality, dialogue, AI behavior
- **Live Testing** - Play your adventure while building
- **JSON Export** - Portable, shareable adventure files

### For Developers

- **Modular Architecture** - Clean, maintainable code
- **Event-Driven** - Loose coupling via event bus
- **Plugin System** - Extend without modifying core
- **99.2% Parser Accuracy** - Comprehensive test suite
- **Full API** - Hook into any system
- **MIT Licensed** - Free to use and modify

## 🎯 Command Examples

The parser understands natural language:

```
> look around
> what am I carrying?
> go north
> get the rusty sword
> examine the old chest
> talk to the merchant
> tell alice to attack the goblin
> eat the bread
> wear the leather armor
> open the wooden door
```

**30 Commands Supported** - Movement, inventory, combat, interaction, and more!

## 📂 Project Structure

```
HB_Eamon/
├── src/acs/              # Source code
│   ├── core/            # Game engine (parser, state, events)
│   ├── systems/         # Game systems (combat, NPCs, environment)
│   ├── ui/              # User interfaces (IDE, launcher)
│   ├── tools/           # Utilities (DSK converter, modding)
│   └── data/            # Data services (config, I/O)
├── scripts/              # Executable scripts
│   ├── acs-ide          # Launch IDE
│   ├── acs-play         # Play adventures
│   └── acs-convert      # Convert DSK files
├── adventures/           # Adventure files (.json)
├── docs/                 # Documentation
├── tests/                # Test suite
├── config/               # Configuration
├── examples/             # Example adventures
├── archive/              # Original Eamon games
├── quickstart.sh         # Quick start menu
├── README.md             # This file
└── LICENSE               # MIT License
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Manual](docs/USER_MANUAL.md) | Complete guide for players and creators |
| [Technical Reference](docs/TECHNICAL_REFERENCE.md) | Architecture, APIs, internals |
| [Quick Start](docs/QUICKSTART.md) | Get up and running in 5 minutes |
| [Command Reference](docs/COMMANDS.md) | All 30 commands with examples |
| [Plugin Guide](docs/PLUGIN_GUIDE.md) | Create custom extensions |
| [Contributing](docs/CONTRIBUTING.md) | How to contribute |

## 🎨 Themes

Choose from 5 professionally designed color schemes:

| Theme | Style | Best For |
|-------|-------|----------|
| **Dark** | Black background, white text | Long sessions, low light |
| **Light** | White background, black text | Daytime, high ambient light |
| **Dracula** | Purple/pink highlights | Stylish dark theme |
| **Nord** | Cool blues and grays | Professional appearance |
| **Monokai** | Warm browns and oranges | Classic editor feel |

Change themes: **View → Theme** in the IDE

## 🔧 Advanced Features

### Achievement System
Track player accomplishments with custom achievements

### Journal System
Automatic quest tracking and game log

### Context-Aware NPCs
NPCs remember past interactions and change behavior

### Dynamic Environment
Weather, lighting, temperature, time of day

### Plugin Support
Extend with custom features without modifying core code

### Modding Support
Load custom content and mechanics

## 📊 Parser Performance

| Metric | Value |
|--------|-------|
| **Test Coverage** | 129 tests across 11 categories |
| **Success Rate** | 99.2% (128/129 passing) |
| **Parse Speed** | <1ms average |
| **Natural Language** | Conversational input supported |

See [Parser Improvements](docs/PARSER_IMPROVEMENTS.md) for details.

## 🛠️ Technology Stack

- **Language**: Python 3.6+
- **UI Framework**: Tkinter (built-in)
- **Data Format**: JSON
- **Architecture**: Modular, event-driven
- **Testing**: Unit and integration tests
- **License**: MIT

## 🎓 Learning Resources

### Tutorials

- **First Adventure** - Create a simple dungeon in 10 minutes
- **Command Mastery** - Learn all 30 commands
- **NPC Design** - Build memorable characters
- **Quest Creation** - Design engaging objectives

### Examples

Sample adventures included:
- `tutorial_quest.json` - Learn the basics
- `sample_adventure.json` - Full-featured example
- `demo_dungeon.json` - Combat-focused

### Community

- **Discord** - Join the community (link in docs)
- **GitHub Issues** - Report bugs, request features
- **Forums** - Share adventures, get help

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:

- Code style guide
- Pull request process
- Testing requirements
- Development setup

## 📜 License

**MIT License**

Copyright © 2025 Honey Badger Universe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

See [LICENSE](LICENSE) for full text.

## 🙏 Credits

### Original Eamon
- Created by **Donald Brown** (1980)
- National Eamon User's Club
- Eamon adventures supported via DSK converter

### Adventure Construction Set
- Developed by **Honey Badger Universe** (2025)
- Built with Python and Tkinter
- Universal adventure creation system

### Special Thanks
- Eamon community for inspiration
- Beta testers and contributors
- Open source community

## 📞 Contact

- **Website**: honeybadgeruniverse.com/eamon
- **Email**: support@honeybadgeruniverse.com
- **GitHub**: github.com/honeybadgeruniverse/eamon-acs

## 🗺️ Roadmap

### Version 2.0 ✅
- [x] Modular architecture
- [x] Natural language parser (99.2% accuracy)
- [x] 5 IDE themes
- [x] Font customization
- [x] Comprehensive documentation
- [x] MIT License

### Version 2.1 (Planned)
- [ ] Spell checker for typos
- [ ] Pronoun support (it, them)
- [ ] Multi-action commands
- [ ] Sound effects
- [ ] Graphics/ASCII art support
- [ ] Online multiplayer

### Version 3.0 (Future)
- [ ] AI-assisted adventure generation
- [ ] Voice input/output
- [ ] Mobile app
- [ ] Web-based IDE
- [ ] Marketplace for adventures

## 🎮 Sample Gameplay

```
=== THE DARK TOWER ===
by Honey Badger Universe

You stand at the entrance of a foreboding tower. Dark clouds 
swirl overhead, and a chill wind howls through the stone archway.
A rusted iron door stands to the north.

Exits: north
Items: torch
NPCs: none

> get torch
You take the wooden torch. It flickers to life in your hand.

> go north
You push through the heavy door...

The Great Hall stretches before you, lit by flickering torches.
Ancient tapestries hang from the walls, depicting battles long 
forgotten. A guard stands at attention near the far door.

Exits: north, south, east
Items: none
NPCs: guard

> talk to guard
Guard: "Halt! State your business in the Dark Tower!"

> examine guard
A stern-looking guard in burnished chainmail. He grips a 
longsword with practiced ease.

> attack guard
The guard readies his weapon!

You hit the guard for 8 damage.
The guard strikes you for 5 damage.
```

## 📈 Statistics

- **30** supported commands
- **5** color themes
- **129** parser tests
- **99.2%** parser accuracy
- **1000+** lines of documentation
- **500+** lines of test code
- **MIT** licensed

---

**Start your adventure today!**

```bash
python3 acs_ide.py
```

*Adventure awaits...*
