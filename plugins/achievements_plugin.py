"""
Achievement System Plugin

Tracks player progress and unlocks achievements based on game events.
This is a refactored, plugin-based version of the original achievement system.
"""

from typing import Dict, List, Any
import logging

from core.base_plugin import BasePlugin, PluginMetadata, PluginPriority
from core.event_bus import Event

# Import the original achievement classes (we're reusing the data structures)
# In a full refactor, these would also be moved to this module
try:
    from acs_achievements import (
        Achievement,
        AchievementCategory,
        PlayerStatistics,
    )
except ImportError:
    # Fallback if module not available
    Achievement = None
    AchievementCategory = None
    PlayerStatistics = None


class AchievementsPlugin(BasePlugin):
    """
    Achievement tracking and statistics plugin

    Features:
    - Tracks player statistics across multiple dimensions
    - Unlocks achievements based on stat thresholds
    - Persists global achievement progress
    - Emits events when achievements unlock

    Events Published:
    - achievement.unlocked: When player earns an achievement
    - stats.updated: When statistics change

    Events Subscribed:
    - game.move: Track movement and exploration
    - combat.victory: Track combat wins
    - combat.defeat: Track deaths
    - item.pickup: Track item collection
    - npc.interaction: Track social stats
    - command.input: Track command usage
    """

    def __init__(self):
        metadata = PluginMetadata(
            name="achievements",
            version="2.0",
            author="ACS Team",
            description="Achievement and statistics tracking system",
            dependencies=[],
            priority=PluginPriority.NORMAL,
            enabled=True,
        )
        super().__init__(metadata)

        self.logger = logging.getLogger("AchievementsPlugin")
        self.achievements: Dict[str, Achievement] = {}
        self.statistics = None

    def initialize(self, state, event_bus, services):
        """Initialize the achievement system"""
        super().initialize(state, event_bus, services)

        # Initialize statistics
        self.statistics = PlayerStatistics() if PlayerStatistics else None

        # Load saved achievements and stats
        self._load_from_state()

        # Register default achievements
        self._register_default_achievements()

        self.logger.info("Achievement system initialized")

    def get_event_subscriptions(self) -> Dict[str, callable]:
        """Subscribe to game events"""
        return {
            "game.move": self.on_move,
            "combat.victory": self.on_combat_victory,
            "combat.defeat": self.on_player_death,
            "item.pickup": self.on_item_pickup,
            "npc.interaction": self.on_npc_interaction,
            "command.input": self.on_command,
        }

    def on_enable(self):
        """Called when plugin is enabled"""
        self.logger.info("Achievement tracking enabled")

    def on_disable(self):
        """Called when plugin is disabled"""
        self._save_to_state()
        self.logger.info("Achievement tracking disabled")

    def shutdown(self):
        """Save data before shutdown"""
        self._save_to_state()

    # Event Handlers

    def on_move(self, event: Event):
        """Handle player movement"""
        if not self.statistics:
            return

        self.statistics.increment("steps_taken")
        self.statistics.increment("rooms_visited")

        # Track unique rooms
        room_id = event.data.get("to_room")
        if room_id:
            self.statistics.add_to_set("unique_rooms_discovered", room_id)

        self._check_achievements()
        self._emit_stats_update()

    def on_combat_victory(self, event: Event):
        """Handle combat victory"""
        if not self.statistics:
            return

        self.statistics.increment("battles_won")
        self.statistics.increment("enemies_defeated")

        damage_dealt = event.data.get("damage_dealt", 0)
        self.statistics.increment("total_damage_dealt", damage_dealt)

        if event.data.get("perfect_battle"):
            self.statistics.increment("perfect_battles")

        self._check_achievements()
        self._emit_stats_update()

    def on_player_death(self, event: Event):
        """Handle player death"""
        if not self.statistics:
            return

        self.statistics.increment("times_died")
        self.statistics.increment("battles_fled")

        self._check_achievements()
        self._emit_stats_update()

    def on_item_pickup(self, event: Event):
        """Handle item collection"""
        if not self.statistics:
            return

        self.statistics.increment("items_collected")

        if event.data.get("is_secret"):
            self.statistics.increment("secrets_discovered")

        gold_value = event.data.get("gold_value", 0)
        if gold_value > 0:
            self.statistics.increment("gold_earned", gold_value)

        self._check_achievements()
        self._emit_stats_update()

    def on_npc_interaction(self, event: Event):
        """Handle NPC interactions"""
        if not self.statistics:
            return

        npc_id = event.data.get("npc_id")
        if npc_id:
            self.statistics.add_to_set("npcs_talked_to", npc_id)

        if event.data.get("quest_completed"):
            self.statistics.increment("quests_completed")

        self._check_achievements()
        self._emit_stats_update()

    def on_command(self, event: Event):
        """Track command usage"""
        if not self.statistics:
            return

        self.statistics.increment("commands_entered")
        self._emit_stats_update()

    # Achievement Management

    def register_achievement(self, achievement: Achievement):
        """Register a new achievement"""
        self.achievements[achievement.id] = achievement
        self.logger.debug(f"Registered achievement: {achievement.name}")

    def unlock_achievement(self, achievement_id: str) -> bool:
        """
        Manually unlock an achievement

        Args:
            achievement_id: ID of achievement to unlock

        Returns:
            True if achievement was newly unlocked
        """
        if achievement_id not in self.achievements:
            return False

        achievement = self.achievements[achievement_id]
        if achievement.unlocked:
            return False

        achievement.unlocked = True
        from datetime import datetime

        achievement.unlock_time = datetime.now()

        # Emit event
        self.event_bus.publish(
            "achievement.unlocked",
            {
                "achievement_id": achievement_id,
                "name": achievement.name,
                "points": achievement.points,
            },
        )

        self.logger.info(f"Achievement unlocked: {achievement.name}")
        return True

    def _check_achievements(self):
        """Check if any achievements should be unlocked"""
        if not self.statistics:
            return

        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue

            # Check stat requirements
            requirements_met = True
            for stat_name, required_value in achievement.stat_requirements.items():
                current_value = self.statistics.get_stat(stat_name)
                if current_value < required_value:
                    requirements_met = False
                    break

            # Check flag requirements
            for flag in achievement.flag_requirements:
                if not self.state.get_flag(flag):
                    requirements_met = False
                    break

            if requirements_met:
                if self.unlock_achievement(achievement.id):
                    newly_unlocked.append(achievement)

        return newly_unlocked

    def _register_default_achievements(self):
        """Register built-in achievements"""
        if not Achievement or not AchievementCategory:
            return

        defaults = [
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
                description="Defeat 20 enemies",
                category=AchievementCategory.COMBAT,
                points=20,
                stat_requirements={"enemies_defeated": 20},
            ),
            Achievement(
                id="socialite",
                name="Socialite",
                description="Talk to 10 different NPCs",
                category=AchievementCategory.SOCIAL,
                points=15,
                stat_requirements={"npcs_talked_to": 10},
            ),
        ]

        for achievement in defaults:
            self.register_achievement(achievement)

    # Persistence

    def _load_from_state(self):
        """Load achievements and stats from game state"""
        # Load statistics
        stats_data = self.state.get_plugin_data(self.metadata.name, "statistics", {})
        if stats_data and PlayerStatistics:
            self.statistics = PlayerStatistics.from_dict(stats_data)

        # Load achievements
        achievement_data = self.state.get_plugin_data(
            self.metadata.name, "achievements", {}
        )
        if achievement_data and Achievement:
            for ach_id, ach_dict in achievement_data.items():
                self.achievements[ach_id] = Achievement.from_dict(ach_dict)

    def _save_to_state(self):
        """Save achievements and stats to game state"""
        if self.statistics:
            self.state.set_plugin_data(
                self.metadata.name, "statistics", self.statistics.to_dict()
            )

        achievement_data = {
            ach_id: ach.to_dict() for ach_id, ach in self.achievements.items()
        }
        self.state.set_plugin_data(self.metadata.name, "achievements", achievement_data)

    def _emit_stats_update(self):
        """Emit stats update event"""
        if self.statistics:
            self.event_bus.publish(
                "stats.updated", {"statistics": self.statistics.to_dict()}
            )

    # Public API

    def get_achievement_summary(self) -> Dict[str, Any]:
        """Get achievement progress summary"""
        total = len(self.achievements)
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        total_points = sum(a.points for a in self.achievements.values() if a.unlocked)

        return {
            "total_achievements": total,
            "unlocked": unlocked,
            "total_points": total_points,
            "completion_percent": (unlocked / total * 100) if total > 0 else 0,
        }

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get key statistics"""
        if not self.statistics:
            return {}

        return {
            "combat": {
                "enemies_defeated": self.statistics.enemies_defeated,
                "battles_won": self.statistics.battles_won,
                "times_died": self.statistics.times_died,
            },
            "exploration": {
                "rooms_visited": self.statistics.rooms_visited,
                "unique_rooms": len(self.statistics.unique_rooms_discovered),
                "steps_taken": self.statistics.steps_taken,
            },
            "social": {
                "npcs_met": len(self.statistics.npcs_talked_to),
                "quests_completed": self.statistics.quests_completed,
            },
        }
