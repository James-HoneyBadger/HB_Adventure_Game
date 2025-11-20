#!/usr/bin/env python3
"""
Adventure Construction Set - Command History & Prediction System
Provides auto-complete, command history, and smart suggestions
"""

from typing import List, Optional, Dict, Any
from collections import deque
import difflib


class CommandHistory:
    """Tracks and provides command history with auto-complete"""

    def __init__(self, max_size: int = 100):
        self.history: deque = deque(maxlen=max_size)
        self.position: int = 0
        self.common_commands: Dict[str, int] = {}

    def add(self, command: str):
        """Add command to history"""
        if command and command.strip():
            self.history.append(command)
            self.position = len(self.history)

            # Track frequency
            cmd_lower = command.lower().strip()
            self.common_commands[cmd_lower] = self.common_commands.get(cmd_lower, 0) + 1

    def get_previous(self) -> Optional[str]:
        """Get previous command (up arrow)"""
        if not self.history or self.position <= 0:
            return None
        self.position -= 1
        return self.history[self.position]

    def get_next(self) -> Optional[str]:
        """Get next command (down arrow)"""
        if not self.history or self.position >= len(self.history) - 1:
            self.position = len(self.history)
            return ""
        self.position += 1
        return self.history[self.position]

    def search(self, prefix: str) -> List[str]:
        """Find commands starting with prefix"""
        prefix_lower = prefix.lower()
        matches = [cmd for cmd in self.history if cmd.lower().startswith(prefix_lower)]
        # Return unique matches in reverse order (most recent first)
        seen = set()
        unique = []
        for cmd in reversed(matches):
            if cmd not in seen:
                seen.add(cmd)
                unique.append(cmd)
        return unique

    def get_most_common(self, limit: int = 10) -> List[tuple]:
        """Get most frequently used commands"""
        sorted_commands = sorted(
            self.common_commands.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_commands[:limit]


class CommandPredictor:
    """Provides intelligent command suggestions"""

    def __init__(self):
        self.context_commands: Dict[str, List[str]] = {
            "combat": ["attack", "flee", "use potion", "cast spell", "defend"],
            "exploration": [
                "look",
                "search",
                "examine",
                "go north",
                "go south",
                "go east",
                "go west",
            ],
            "inventory": ["get", "drop", "inventory", "equip", "unequip"],
            "social": ["talk to", "give", "trade", "recruit", "party"],
            "general": ["status", "help", "save", "quit"],
        }

        self.typo_corrections: Dict[str, str] = {
            "atack": "attack",
            "attak": "attack",
            "attck": "attack",
            "lok": "look",
            "loook": "look",
            "inventry": "inventory",
            "inventroy": "inventory",
            "nroth": "north",
            "soth": "south",
            "esst": "east",
            "wset": "west",
            "examne": "examine",
            "exmine": "examine",
            "serach": "search",
            "saerch": "search",
        }

    def suggest_completions(self, partial: str, all_commands: List[str]) -> List[str]:
        """Suggest command completions"""
        if not partial:
            return []

        partial_lower = partial.lower()

        # Check for exact typo correction
        if partial_lower in self.typo_corrections:
            return [self.typo_corrections[partial_lower]]

        # Find matching commands
        matches = [cmd for cmd in all_commands if cmd.lower().startswith(partial_lower)]

        if matches:
            return matches[:5]  # Top 5 matches

        # Try fuzzy matching for typos
        close_matches = difflib.get_close_matches(
            partial_lower, all_commands, n=3, cutoff=0.6
        )

        return close_matches

    def suggest_based_on_context(self, context: str) -> List[str]:
        """Suggest commands based on current context"""
        return self.context_commands.get(context, [])

    def fix_typo(self, command: str) -> str:
        """Attempt to fix typo in command"""
        words = command.lower().split()
        if not words:
            return command

        first_word = words[0]

        # Check known typos
        if first_word in self.typo_corrections:
            words[0] = self.typo_corrections[first_word]
            return " ".join(words)

        return command


class CommandMacro:
    """Allows creating shortcuts for complex commands"""

    def __init__(self):
        self.macros: Dict[str, List[str]] = {}

    def add_macro(self, name: str, commands: List[str]):
        """Create a macro"""
        self.macros[name] = commands

    def get_macro(self, name: str) -> Optional[List[str]]:
        """Get macro commands"""
        return self.macros.get(name)

    def remove_macro(self, name: str) -> bool:
        """Remove a macro"""
        if name in self.macros:
            del self.macros[name]
            return True
        return False

    def list_macros(self) -> List[str]:
        """List all macro names"""
        return list(self.macros.keys())

    def is_macro(self, command: str) -> bool:
        """Check if command is a macro"""
        return command.strip() in self.macros


class SmartCommandSystem:
    """Complete command enhancement system"""

    def __init__(self):
        self.history = CommandHistory()
        self.predictor = CommandPredictor()
        self.macros = CommandMacro()

        # Base command list for suggestions
        self.base_commands = [
            "north",
            "south",
            "east",
            "west",
            "up",
            "down",
            "look",
            "examine",
            "search",
            "inventory",
            "get",
            "drop",
            "take",
            "put",
            "attack",
            "flee",
            "defend",
            "talk",
            "give",
            "trade",
            "use",
            "equip",
            "unequip",
            "wear",
            "remove",
            "open",
            "close",
            "unlock",
            "read",
            "drink",
            "eat",
            "save",
            "load",
            "quit",
            "help",
            "status",
            "quests",
            "party",
            "recruit",
        ]

    def process_input(self, user_input: str) -> str:
        """Process user input with typo correction"""
        # Check if it's a macro
        if self.macros.is_macro(user_input):
            return user_input  # Will be expanded by engine

        # Try typo correction
        corrected = self.predictor.fix_typo(user_input)

        if corrected != user_input:
            return corrected

        return user_input

    def add_to_history(self, command: str):
        """Add command to history"""
        self.history.add(command)

    def get_suggestions(self, partial: str, context: str = "general") -> List[str]:
        """Get command suggestions"""
        # Get completions
        completions = self.predictor.suggest_completions(partial, self.base_commands)

        # Add history-based suggestions
        history_matches = self.history.search(partial)

        # Combine and deduplicate
        all_suggestions = list(dict.fromkeys(completions + history_matches))

        # If no matches, suggest context-based commands
        if not all_suggestions and not partial:
            all_suggestions = self.predictor.suggest_based_on_context(context)

        return all_suggestions[:5]  # Top 5

    def create_macro(self, name: str, commands: List[str]):
        """Create a command macro"""
        self.macros.add_macro(name, commands)

    def execute_macro(self, name: str) -> Optional[List[str]]:
        """Get commands from macro"""
        return self.macros.get_macro(name)
