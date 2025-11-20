#!/usr/bin/env python3
"""
Adventure Construction Set - Accessibility Features
Difficulty settings, display options, and inclusive design
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class DifficultyLevel(Enum):
    """Game difficulty settings"""

    STORY = "story"  # Very easy, focus on narrative
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    BRUTAL = "brutal"  # Permadeath, limited resources


class TextSize(Enum):
    """Text size options"""

    SMALL = "small"
    NORMAL = "normal"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class ColorScheme(Enum):
    """Color palette options"""

    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    DEUTERANOPIA = "deuteranopia"  # Red-green colorblind
    PROTANOPIA = "protanopia"  # Another red-green variant
    TRITANOPIA = "tritanopia"  # Blue-yellow colorblind
    MONOCHROME = "monochrome"


@dataclass
class DifficultySettings:
    """Settings that change based on difficulty"""

    level: DifficultyLevel

    # Combat modifiers
    player_damage_multiplier: float = 1.0
    enemy_damage_multiplier: float = 1.0
    player_health_multiplier: float = 1.0
    critical_hit_chance: float = 0.1

    # Resource availability
    item_spawn_rate: float = 1.0
    gold_multiplier: float = 1.0
    healing_effectiveness: float = 1.0

    # Game mechanics
    permadeath: bool = False
    autosave: bool = True
    save_limit: Optional[int] = None
    hint_frequency: float = 1.0
    tutorial_enabled: bool = True

    @staticmethod
    def from_difficulty(level: DifficultyLevel) -> "DifficultySettings":
        """Create settings based on difficulty level"""
        settings = DifficultySettings(level)

        if level == DifficultyLevel.STORY:
            settings.player_damage_multiplier = 1.5
            settings.enemy_damage_multiplier = 0.5
            settings.player_health_multiplier = 1.5
            settings.healing_effectiveness = 1.5
            settings.item_spawn_rate = 1.5
            settings.gold_multiplier = 1.5
            settings.hint_frequency = 1.5

        elif level == DifficultyLevel.EASY:
            settings.player_damage_multiplier = 1.2
            settings.enemy_damage_multiplier = 0.8
            settings.player_health_multiplier = 1.2
            settings.item_spawn_rate = 1.2
            settings.hint_frequency = 1.2

        elif level == DifficultyLevel.NORMAL:
            # Default values
            pass

        elif level == DifficultyLevel.HARD:
            settings.player_damage_multiplier = 0.8
            settings.enemy_damage_multiplier = 1.3
            settings.player_health_multiplier = 0.8
            settings.critical_hit_chance = 0.05
            settings.item_spawn_rate = 0.7
            settings.gold_multiplier = 0.7
            settings.hint_frequency = 0.5
            settings.tutorial_enabled = False

        elif level == DifficultyLevel.BRUTAL:
            settings.player_damage_multiplier = 0.6
            settings.enemy_damage_multiplier = 1.5
            settings.player_health_multiplier = 0.6
            settings.critical_hit_chance = 0.05
            settings.item_spawn_rate = 0.5
            settings.gold_multiplier = 0.5
            settings.healing_effectiveness = 0.7
            settings.permadeath = True
            settings.save_limit = 3
            settings.hint_frequency = 0.0
            settings.tutorial_enabled = False

        return settings


@dataclass
class DisplayOptions:
    """Visual and text display settings"""

    text_size: TextSize = TextSize.NORMAL
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    use_colors: bool = True
    use_emoji: bool = True
    show_health_bar: bool = True
    show_minimap: bool = True

    # Screen reader support
    screen_reader_mode: bool = False
    verbose_descriptions: bool = False
    announce_room_changes: bool = False

    # Text display
    word_wrap: bool = True
    column_width: int = 80
    paragraph_spacing: int = 1

    # UI elements
    show_compass: bool = True
    show_status_line: bool = True
    show_inventory_count: bool = True
    show_quest_tracker: bool = True

    def get_text_width(self) -> int:
        """Get text width based on size setting"""
        widths = {
            TextSize.SMALL: 100,
            TextSize.NORMAL: 80,
            TextSize.LARGE: 60,
            TextSize.EXTRA_LARGE: 50,
        }
        return widths.get(self.text_size, 80)


class ColorPalette:
    """Color codes for different schemes"""

    # ANSI color codes
    RESET = "\033[0m"

    # Default colors
    DEFAULT = {
        "error": "\033[91m",  # Red
        "warning": "\033[93m",  # Yellow
        "success": "\033[92m",  # Green
        "info": "\033[94m",  # Blue
        "highlight": "\033[95m",  # Magenta
        "dim": "\033[90m",  # Gray
        "bold": "\033[1m",
    }

    # High contrast
    HIGH_CONTRAST = {
        "error": "\033[97;41m",  # White on red
        "warning": "\033[30;43m",  # Black on yellow
        "success": "\033[30;42m",  # Black on green
        "info": "\033[97;44m",  # White on blue
        "highlight": "\033[97;45m",  # White on magenta
        "dim": "\033[37m",  # Light gray
        "bold": "\033[1;97m",  # Bold white
    }

    # Monochrome (no colors, just bold/dim)
    MONOCHROME = {
        "error": "\033[1m",
        "warning": "\033[1m",
        "success": "\033[1m",
        "info": "",
        "highlight": "\033[1m",
        "dim": "\033[2m",
        "bold": "\033[1m",
    }

    @staticmethod
    def get_palette(scheme: ColorScheme) -> Dict[str, str]:
        """Get color palette for scheme"""
        if scheme == ColorScheme.DEFAULT:
            return ColorPalette.DEFAULT
        elif scheme == ColorScheme.HIGH_CONTRAST:
            return ColorPalette.HIGH_CONTRAST
        elif scheme == ColorScheme.MONOCHROME:
            return ColorPalette.MONOCHROME
        else:
            # Colorblind modes use modified default
            # (would need more sophisticated color adjustments)
            return ColorPalette.DEFAULT


class AccessibilitySystem:
    """Manages accessibility options"""

    def __init__(self):
        self.difficulty = DifficultySettings.from_difficulty(DifficultyLevel.NORMAL)
        self.display = DisplayOptions()
        self.palette = ColorPalette.get_palette(ColorScheme.DEFAULT)

        # Simplified mode settings
        self.simplified_mode = False
        self.auto_suggest = True
        self.confirm_dangerous = True

    def set_difficulty(self, level: DifficultyLevel):
        """Change difficulty level"""
        self.difficulty = DifficultySettings.from_difficulty(level)

    def set_color_scheme(self, scheme: ColorScheme):
        """Change color scheme"""
        self.display.color_scheme = scheme
        self.palette = ColorPalette.get_palette(scheme)

    def enable_screen_reader_mode(self):
        """Optimize for screen readers"""
        self.display.screen_reader_mode = True
        self.display.use_colors = False
        self.display.use_emoji = False
        self.display.verbose_descriptions = True
        self.display.announce_room_changes = True
        self.display.show_health_bar = False
        self.display.show_minimap = False

    def enable_simplified_mode(self):
        """Enable simplified UI for beginners"""
        self.simplified_mode = True
        self.auto_suggest = True
        self.display.show_compass = True
        self.display.show_quest_tracker = True
        self.display.show_inventory_count = True

    def colorize(self, text: str, color_type: str) -> str:
        """Apply color to text if enabled"""
        if not self.display.use_colors:
            return text

        color = self.palette.get(color_type, "")
        if color:
            return f"{color}{text}{ColorPalette.RESET}"
        return text

    def format_text(self, text: str) -> str:
        """Format text according to display settings"""
        if self.display.word_wrap:
            # Simple word wrap
            width = self.display.get_text_width()
            lines = []
            for paragraph in text.split("\n"):
                if len(paragraph) <= width:
                    lines.append(paragraph)
                else:
                    # Wrap long lines
                    words = paragraph.split()
                    current_line = []
                    current_length = 0

                    for word in words:
                        word_len = len(word) + 1
                        if current_length + word_len > width:
                            lines.append(" ".join(current_line))
                            current_line = [word]
                            current_length = word_len
                        else:
                            current_line.append(word)
                            current_length += word_len

                    if current_line:
                        lines.append(" ".join(current_line))

            # Add paragraph spacing
            spacing = "\n" * self.display.paragraph_spacing
            return spacing.join(lines)
        return text

    def format_health_bar(self, current: int, maximum: int, width: int = 20) -> str:
        """Create a text health bar"""
        if not self.display.show_health_bar:
            return f"HP: {current}/{maximum}"

        if self.display.screen_reader_mode:
            percentage = int((current / maximum) * 100)
            return f"Health: {current} out of {maximum} ({percentage}%)"

        filled = int((current / maximum) * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty
        percentage = int((current / maximum) * 100)

        # Color code based on health
        if percentage > 60:
            bar = self.colorize(bar, "success")
        elif percentage > 30:
            bar = self.colorize(bar, "warning")
        else:
            bar = self.colorize(bar, "error")

        return f"[{bar}] {current}/{maximum}"

    def format_compass(self, exits: List[str]) -> str:
        """Format compass showing available exits"""
        if not self.display.show_compass:
            return ""

        if self.display.screen_reader_mode:
            if exits:
                return f"Available exits: {', '.join(exits)}"
            return "No visible exits"

        # Visual compass
        compass = {
            "north": "↑",
            "south": "↓",
            "east": "→",
            "west": "←",
            "up": "⬆",
            "down": "⬇",
            "n": "↑",
            "s": "↓",
            "e": "→",
            "w": "←",
            "u": "⬆",
            "d": "⬇",
        }

        if not self.display.use_emoji:
            compass = {k: k[0].upper() for k in compass.keys()}

        symbols = [compass.get(e.lower(), e[0]) for e in exits]
        return f"Exits: {' '.join(symbols)}"

    def get_command_suggestions(self, context: str) -> List[str]:
        """Get suggested commands for context"""
        if not self.auto_suggest or not self.simplified_mode:
            return []

        suggestions = {
            "start": [
                "look - See your surroundings",
                "inventory - Check what you have",
                "north/south/east/west - Move around",
            ],
            "combat": [
                "attack [enemy] - Fight an enemy",
                "flee - Run away from combat",
                "use [item] - Use an item",
            ],
            "npc": [
                "talk to [name] - Start a conversation",
                "give [item] to [name] - Give an item",
                "recruit [name] - Ask to join party",
            ],
        }

        return suggestions.get(context, [])

    def confirm_action(self, action: str) -> str:
        """Get confirmation prompt for dangerous actions"""
        if not self.confirm_dangerous:
            return None

        dangerous = ["attack", "drop", "sell", "quit", "delete"]
        if any(d in action.lower() for d in dangerous):
            return f"Are you sure you want to {action}? (yes/no)"
        return None

    def to_dict(self) -> Dict:
        """Serialize accessibility settings"""
        return {
            "difficulty_level": self.difficulty.level.value,
            "text_size": self.display.text_size.value,
            "color_scheme": self.display.color_scheme.value,
            "use_colors": self.display.use_colors,
            "use_emoji": self.display.use_emoji,
            "screen_reader_mode": self.display.screen_reader_mode,
            "simplified_mode": self.simplified_mode,
            "auto_suggest": self.auto_suggest,
            "confirm_dangerous": self.confirm_dangerous,
        }

    def from_dict(self, data: Dict):
        """Restore accessibility settings"""
        if "difficulty_level" in data:
            level = DifficultyLevel(data["difficulty_level"])
            self.set_difficulty(level)

        if "color_scheme" in data:
            scheme = ColorScheme(data["color_scheme"])
            self.set_color_scheme(scheme)

        if "text_size" in data:
            self.display.text_size = TextSize(data["text_size"])

        self.display.use_colors = data.get("use_colors", True)
        self.display.use_emoji = data.get("use_emoji", True)
        self.display.screen_reader_mode = data.get("screen_reader_mode", False)
        self.simplified_mode = data.get("simplified_mode", False)
        self.auto_suggest = data.get("auto_suggest", True)
        self.confirm_dangerous = data.get("confirm_dangerous", True)

        # Apply screen reader mode if enabled
        if self.display.screen_reader_mode:
            self.enable_screen_reader_mode()
