"""
Centralized game state management

GameState holds all game data and provides controlled access to it.
This makes it easier to save/load, debug, and reason about state changes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class GamePhase(Enum):
    """Current phase of the game"""

    MENU = "menu"
    INTRO = "intro"
    PLAYING = "playing"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    PAUSED = "paused"
    GAME_OVER = "game_over"


@dataclass
class PlayerState:
    """Player character state"""

    name: str = "Adventurer"
    hardiness: int = 10
    agility: int = 10
    charisma: int = 10
    strength_current: int = 20
    strength_max: int = 20
    gold: int = 100
    experience: int = 0
    current_room: int = 1
    weapon_ability: Dict[int, int] = field(default_factory=dict)
    armor_expertise: int = 0
    inventory: List[int] = field(default_factory=list)  # Item IDs
    worn_items: List[int] = field(default_factory=list)  # Item IDs
    weapon_ids: List[int] = field(default_factory=list)  # Ready weapons

    def __post_init__(self):
        """Initialize default weapon abilities"""
        if not self.weapon_ability:
            # Default abilities for weapon types 1-5
            self.weapon_ability = {i: 0 for i in range(1, 6)}


@dataclass
class GameState:
    """
    Central repository for all game state

    Attributes:
        phase: Current game phase
        player: Player character state
        rooms: Room data by ID
        items: Item data by ID
        monsters: Monster data by ID
        custom_data: Plugin-specific data storage
        flags: Global game flags
        turn_count: Number of turns elapsed
    """

    phase: GamePhase = GamePhase.MENU
    player: PlayerState = field(default_factory=PlayerState)
    rooms: Dict[int, Any] = field(default_factory=dict)
    items: Dict[int, Any] = field(default_factory=dict)
    monsters: Dict[int, Any] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)
    turn_count: int = 0
    adventure_name: str = ""
    adventure_author: str = ""

    def get_plugin_data(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """
        Get plugin-specific data

        Args:
            plugin_name: Name of the plugin
            key: Data key
            default: Default value if not found

        Returns:
            Stored value or default
        """
        if plugin_name not in self.custom_data:
            self.custom_data[plugin_name] = {}
        return self.custom_data[plugin_name].get(key, default)

    def set_plugin_data(self, plugin_name: str, key: str, value: Any):
        """
        Set plugin-specific data

        Args:
            plugin_name: Name of the plugin
            key: Data key
            value: Value to store
        """
        if plugin_name not in self.custom_data:
            self.custom_data[plugin_name] = {}
        self.custom_data[plugin_name][key] = value

    def get_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get a global game flag"""
        return self.flags.get(flag_name, default)

    def set_flag(self, flag_name: str, value: bool):
        """Set a global game flag"""
        self.flags[flag_name] = value

    def increment_turn(self):
        """Increment the turn counter"""
        self.turn_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "phase": self.phase.value,
            "player": {
                "name": self.player.name,
                "hardiness": self.player.hardiness,
                "agility": self.player.agility,
                "charisma": self.player.charisma,
                "strength_current": self.player.strength_current,
                "strength_max": self.player.strength_max,
                "gold": self.player.gold,
                "experience": self.player.experience,
                "current_room": self.player.current_room,
                "weapon_ability": self.player.weapon_ability,
                "armor_expertise": self.player.armor_expertise,
                "inventory": self.player.inventory,
                "worn_items": self.player.worn_items,
                "weapon_ids": self.player.weapon_ids,
            },
            "rooms": self.rooms,
            "items": self.items,
            "monsters": self.monsters,
            "custom_data": self.custom_data,
            "flags": self.flags,
            "turn_count": self.turn_count,
            "adventure_name": self.adventure_name,
            "adventure_author": self.adventure_author,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Create state from dictionary"""
        player_data = data.get("player", {})
        player = PlayerState(
            name=player_data.get("name", "Adventurer"),
            hardiness=player_data.get("hardiness", 10),
            agility=player_data.get("agility", 10),
            charisma=player_data.get("charisma", 10),
            strength_current=player_data.get("strength_current", 20),
            strength_max=player_data.get("strength_max", 20),
            gold=player_data.get("gold", 100),
            experience=player_data.get("experience", 0),
            current_room=player_data.get("current_room", 1),
            weapon_ability=player_data.get("weapon_ability", {}),
            armor_expertise=player_data.get("armor_expertise", 0),
            inventory=player_data.get("inventory", []),
            worn_items=player_data.get("worn_items", []),
            weapon_ids=player_data.get("weapon_ids", []),
        )

        phase_str = data.get("phase", "menu")
        phase = GamePhase(phase_str)

        return cls(
            phase=phase,
            player=player,
            rooms=data.get("rooms", {}),
            items=data.get("items", {}),
            monsters=data.get("monsters", {}),
            custom_data=data.get("custom_data", {}),
            flags=data.get("flags", {}),
            turn_count=data.get("turn_count", 0),
            adventure_name=data.get("adventure_name", ""),
            adventure_author=data.get("adventure_author", ""),
        )
