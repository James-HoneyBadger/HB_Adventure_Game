#!/usr/bin/env python3
"""
Adventure Construction Set - Achievement & Statistics System
Tracks player progress, unlocks achievements, and maintains statistics
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class AchievementCategory(Enum):
    """Categories for organizing achievements"""

    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    COMPLETION = "completion"
    SPECIAL = "special"
    SECRET = "secret"


@dataclass
class Achievement:
    """Represents an unlockable achievement"""

    id: str
    name: str
    description: str
    category: AchievementCategory
    points: int = 10
    hidden: bool = False  # Don't show until unlocked
    unlocked: bool = False
    unlock_time: Optional[datetime] = None

    # Unlock conditions
    stat_requirements: Dict[str, int] = field(default_factory=dict)
    flag_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize achievement"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "points": self.points,
            "hidden": self.hidden,
            "unlocked": self.unlocked,
            "unlock_time": (self.unlock_time.isoformat() if self.unlock_time else None),
            "stat_requirements": self.stat_requirements,
            "flag_requirements": self.flag_requirements,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Deserialize achievement"""
        achievement = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=AchievementCategory(data["category"]),
            points=data.get("points", 10),
            hidden=data.get("hidden", False),
            unlocked=data.get("unlocked", False),
            stat_requirements=data.get("stat_requirements", {}),
            flag_requirements=data.get("flag_requirements", []),
        )
        if data.get("unlock_time"):
            achievement.unlock_time = datetime.fromisoformat(data["unlock_time"])
        return achievement


class PlayerStatistics:
    """Comprehensive player statistics tracking"""

    def __init__(self):
        # Combat stats
        self.enemies_defeated = 0
        self.total_damage_dealt = 0
        self.total_damage_taken = 0
        self.critical_hits = 0
        self.times_died = 0
        self.battles_won = 0
        self.battles_fled = 0

        # Exploration stats
        self.rooms_visited = 0
        self.unique_rooms_discovered = set()
        self.steps_taken = 0
        self.items_found = 0
        self.secrets_discovered = 0
        self.doors_opened = 0
        self.traps_triggered = 0

        # Social stats
        self.npcs_talked_to = set()
        self.quests_completed = 0
        self.quests_failed = 0
        self.companions_recruited = 0
        self.items_traded = 0

        # Item stats
        self.items_collected = 0
        self.gold_earned = 0
        self.gold_spent = 0
        self.items_used = 0
        self.items_dropped = 0

        # Time stats
        self.play_time_seconds = 0
        self.turns_taken = 0
        self.commands_entered = 0
        self.saves_made = 0

        # Special stats
        self.highest_combo = 0
        self.longest_exploration_streak = 0
        self.perfect_battles = 0  # No damage taken

    def increment(self, stat_name: str, amount: int = 1):
        """Increment a statistic"""
        if hasattr(self, stat_name):
            current = getattr(self, stat_name)
            if isinstance(current, (int, float)):
                setattr(self, stat_name, current + amount)

    def add_to_set(self, stat_name: str, value: Any):
        """Add value to a set-based stat"""
        if hasattr(self, stat_name):
            current = getattr(self, stat_name)
            if isinstance(current, set):
                current.add(value)

    def get_stat(self, stat_name: str) -> Any:
        """Get a statistic value"""
        if hasattr(self, stat_name):
            value = getattr(self, stat_name)
            # Convert sets to counts for display
            if isinstance(value, set):
                return len(value)
            return value
        return 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize statistics"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, set):
                data[key] = list(value)
            else:
                data[key] = value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlayerStatistics":
        """Deserialize statistics"""
        stats = cls()
        for key, value in data.items():
            if hasattr(stats, key):
                current = getattr(stats, key)
                if isinstance(current, set):
                    setattr(stats, key, set(value))
                else:
                    setattr(stats, key, value)
        return stats


class AchievementSystem:
    """Manages achievements and statistics"""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.statistics = PlayerStatistics()
        self.custom_flags: Dict[str, bool] = {}
        self.global_stats_file = "player_global_stats.json"

        # Register default achievements
        self._register_default_achievements()

    def _register_default_achievements(self):
        """Register built-in achievements"""
        default_achievements = [
            Achievement(
                id="first_steps",
                name="First Steps",
                description="Take your first steps in adventure",
                category=AchievementCategory.EXPLORATION,
                points=5,
                stat_requirements={"steps_taken": 1},
            ),
            Achievement(
                id="explorer",
                name="Explorer",
                description="Discover 10 unique locations",
                category=AchievementCategory.EXPLORATION,
                points=15,
                stat_requirements={"unique_rooms_discovered": 10},
            ),
            Achievement(
                id="warrior",
                name="Warrior",
                description="Defeat 10 enemies",
                category=AchievementCategory.COMBAT,
                points=20,
                stat_requirements={"enemies_defeated": 10},
            ),
            Achievement(
                id="veteran",
                name="Veteran",
                description="Defeat 50 enemies",
                category=AchievementCategory.COMBAT,
                points=50,
                stat_requirements={"enemies_defeated": 50},
            ),
            Achievement(
                id="socialite",
                name="Socialite",
                description="Talk to 10 different NPCs",
                category=AchievementCategory.SOCIAL,
                points=15,
                stat_requirements={"npcs_talked_to": 10},
            ),
            Achievement(
                id="quest_master",
                name="Quest Master",
                description="Complete 5 quests",
                category=AchievementCategory.COMPLETION,
                points=25,
                stat_requirements={"quests_completed": 5},
            ),
            Achievement(
                id="critical_master",
                name="Critical Strike Master",
                description="Land 20 critical hits",
                category=AchievementCategory.COMBAT,
                points=20,
                stat_requirements={"critical_hits": 20},
            ),
            Achievement(
                id="treasure_hunter",
                name="Treasure Hunter",
                description="Collect 100 items",
                category=AchievementCategory.EXPLORATION,
                points=30,
                stat_requirements={"items_collected": 100},
            ),
            Achievement(
                id="wealthy",
                name="Wealthy",
                description="Accumulate 1000 gold pieces",
                category=AchievementCategory.SPECIAL,
                points=25,
                stat_requirements={"gold_earned": 1000},
            ),
            Achievement(
                id="survivor",
                name="Survivor",
                description="Win 10 battles without dying",
                category=AchievementCategory.COMBAT,
                points=40,
                stat_requirements={"battles_won": 10, "times_died": 0},
            ),
            Achievement(
                id="speedrunner",
                name="Speedrunner",
                description="Complete adventure in under 500 turns",
                category=AchievementCategory.SPECIAL,
                points=50,
                hidden=True,
                stat_requirements={"turns_taken": 500},
            ),
            Achievement(
                id="pacifist",
                name="Pacifist",
                description="Complete adventure without killing anyone",
                category=AchievementCategory.SPECIAL,
                points=100,
                hidden=True,
                stat_requirements={"enemies_defeated": 0},
            ),
        ]

        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement

    def register_achievement(self, achievement: Achievement):
        """Register a custom achievement"""
        self.achievements[achievement.id] = achievement

    def check_achievements(self) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue

            # Check stat requirements
            stats_met = True
            for stat_name, required_value in achievement.stat_requirements.items():
                current_value = self.statistics.get_stat(stat_name)
                if current_value < required_value:
                    stats_met = False
                    break

            # Check flag requirements
            flags_met = all(
                self.custom_flags.get(flag, False)
                for flag in achievement.flag_requirements
            )

            # Unlock if all requirements met
            if stats_met and flags_met:
                achievement.unlocked = True
                achievement.unlock_time = datetime.now()
                newly_unlocked.append(achievement)

        return newly_unlocked

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Manually unlock an achievement"""
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            if not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlock_time = datetime.now()
                return True
        return False

    def set_flag(self, flag_name: str, value: bool = True):
        """Set a custom achievement flag"""
        self.custom_flags[flag_name] = value

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get achievement progress summary"""
        total = len(self.achievements)
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        total_points = sum(a.points for a in self.achievements.values())
        earned_points = sum(a.points for a in self.achievements.values() if a.unlocked)

        return {
            "total_achievements": total,
            "unlocked_achievements": unlocked,
            "completion_percent": (unlocked / total * 100) if total > 0 else 0,
            "total_points": total_points,
            "earned_points": earned_points,
        }

    def get_achievements_by_category(
        self, category: AchievementCategory
    ) -> List[Achievement]:
        """Get achievements in a category"""
        return [a for a in self.achievements.values() if a.category == category]

    def get_visible_achievements(self) -> List[Achievement]:
        """Get achievements that should be shown to player"""
        return [a for a in self.achievements.values() if not a.hidden or a.unlocked]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize achievement system"""
        return {
            "achievements": {aid: a.to_dict() for aid, a in self.achievements.items()},
            "statistics": self.statistics.to_dict(),
            "custom_flags": self.custom_flags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AchievementSystem":
        """Deserialize achievement system"""
        system = cls()

        # Load achievements
        for aid, adata in data.get("achievements", {}).items():
            system.achievements[aid] = Achievement.from_dict(adata)

        # Load statistics
        if "statistics" in data:
            system.statistics = PlayerStatistics.from_dict(data["statistics"])

        # Load flags
        system.custom_flags = data.get("custom_flags", {})

        return system

    def save_global_stats(self):
        """Save statistics to global file"""
        try:
            with open(self.global_stats_file, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save global stats: {e}")

    def load_global_stats(self):
        """Load statistics from global file"""
        try:
            with open(self.global_stats_file, "r") as f:
                data = json.load(f)
                loaded = self.from_dict(data)
                self.achievements = loaded.achievements
                self.statistics = loaded.statistics
                self.custom_flags = loaded.custom_flags
        except FileNotFoundError:
            pass  # No global stats yet
        except Exception as e:
            print(f"Warning: Could not load global stats: {e}")
