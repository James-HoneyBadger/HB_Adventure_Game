#!/usr/bin/env python3
"""
Adventure Construction Set - Tutorial & Contextual Help System
Progressive feature discovery, contextual hints, and example commands
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class TutorialStage(Enum):
    """Progression stages for tutorial"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FeatureCategory(Enum):
    """Categories of features to introduce"""

    MOVEMENT = "movement"
    COMBAT = "combat"
    INVENTORY = "inventory"
    INTERACTION = "interaction"
    PARTY = "party"
    ADVANCED = "advanced"


@dataclass
class Tutorial:
    """A tutorial message for a specific feature"""

    id: str
    category: FeatureCategory
    stage: TutorialStage
    title: str
    message: str
    example_commands: List[str]
    trigger_condition: str  # What triggers this tutorial
    shown: bool = False


class ContextualHintSystem:
    """Provides context-aware hints and tutorials"""

    def __init__(self):
        self.tutorials: Dict[str, Tutorial] = {}
        self.shown_tutorials: Set[str] = set()
        self.discovered_features: Set[str] = set()
        self.hint_frequency = 0.3  # 30% chance to show hints
        self.tutorial_stage = TutorialStage.BEGINNER

        self._register_default_tutorials()

    def _register_default_tutorials(self):
        """Register built-in tutorials"""
        tutorials = [
            # Beginner - Movement
            Tutorial(
                "movement_basic",
                FeatureCategory.MOVEMENT,
                TutorialStage.BEGINNER,
                "Moving Around",
                "You can move by typing directions like 'north', 'south', "
                "'east', 'west' (or just 'n', 's', 'e', 'w').",
                ["north", "south", "go east", "move west"],
                "first_room",
            ),
            # Beginner - Looking
            Tutorial(
                "looking",
                FeatureCategory.MOVEMENT,
                TutorialStage.BEGINNER,
                "Looking Around",
                "Type 'look' to see your surroundings. You can also examine "
                "specific things.",
                ["look", "examine sword", "look at painting"],
                "first_look",
            ),
            # Beginner - Inventory
            Tutorial(
                "inventory_basic",
                FeatureCategory.INVENTORY,
                TutorialStage.BEGINNER,
                "Managing Items",
                "Use 'get' to pick up items and 'drop' to put them down. "
                "Type 'inventory' or 'i' to see what you're carrying.",
                ["get sword", "drop torch", "inventory"],
                "first_item",
            ),
            # Beginner - Combat
            Tutorial(
                "combat_basic",
                FeatureCategory.COMBAT,
                TutorialStage.BEGINNER,
                "Fighting Enemies",
                "When you encounter enemies, use 'attack [enemy]' to fight. "
                "You can also 'flee' if things get dangerous!",
                ["attack goblin", "flee", "status"],
                "first_enemy",
            ),
            # Intermediate - Talking
            Tutorial(
                "interaction_talk",
                FeatureCategory.INTERACTION,
                TutorialStage.INTERMEDIATE,
                "Talking to NPCs",
                "You can talk to NPCs to learn information. "
                "Try 'talk to [name]' or 'ask [name] about [topic]'.",
                ["talk to wizard", "ask guard about quest"],
                "first_npc",
            ),
            # Intermediate - Equipment
            Tutorial(
                "equipment",
                FeatureCategory.INVENTORY,
                TutorialStage.INTERMEDIATE,
                "Using Equipment",
                "Equip weapons and armor to improve your combat abilities. "
                "Use 'equip [item]' and 'unequip [item]'.",
                ["equip sword", "equip shield", "unequip helmet"],
                "found_equipment",
            ),
            # Advanced - Party
            Tutorial(
                "party_recruit",
                FeatureCategory.PARTY,
                TutorialStage.ADVANCED,
                "Recruiting Companions",
                "You can recruit friendly NPCs to join your party! "
                "Use 'recruit [name]' to add them to your team.",
                ["recruit marcus", "party", "tell marcus to wait"],
                "first_recruitment",
            ),
            # Advanced - Natural Language
            Tutorial(
                "natural_language",
                FeatureCategory.ADVANCED,
                TutorialStage.ADVANCED,
                "Natural Language Commands",
                "You can type commands naturally! Instead of cryptic syntax, "
                "try sentences like 'Can I pick up the sword?'",
                [
                    "Can I go north?",
                    "I want to talk to the wizard",
                    "Please show me my inventory",
                ],
                "used_simple_command",
            ),
            # Expert - Advanced Party
            Tutorial(
                "party_tactics",
                FeatureCategory.PARTY,
                TutorialStage.EXPERT,
                "Advanced Party Tactics",
                "Control your companions' behavior with stances. "
                "Tell them to be aggressive, defensive, or supportive!",
                [
                    "tell marcus to be aggressive",
                    "tell sarah to be defensive",
                    "gather party",
                ],
                "has_companions",
            ),
        ]

        for tutorial in tutorials:
            self.tutorials[tutorial.id] = tutorial

    def check_and_show_hint(
        self, context: str, stats: Dict[str, int]
    ) -> Optional[Tutorial]:
        """Check if hint should be shown based on context"""
        import random

        if random.random() > self.hint_frequency:
            return None

        # Find relevant unshown tutorials
        candidates = []
        for tutorial in self.tutorials.values():
            if tutorial.shown or tutorial.id in self.shown_tutorials:
                continue
            if tutorial.stage.value != self.tutorial_stage.value:
                continue
            if self._check_trigger(tutorial.trigger_condition, context, stats):
                candidates.append(tutorial)

        if candidates:
            # Pick most relevant
            return candidates[0]
        return None

    def _check_trigger(self, trigger: str, context: str, stats: Dict[str, int]) -> bool:
        """Check if tutorial trigger condition is met"""
        # Simple trigger matching (can be enhanced)
        if trigger == "first_room":
            return context == "moved" and stats.get("rooms_visited", 0) == 1
        elif trigger == "first_look":
            return context == "looked"
        elif trigger == "first_item":
            return context == "got_item"
        elif trigger == "first_enemy":
            return context == "combat_start"
        elif trigger == "first_npc":
            return context == "saw_npc"
        elif trigger == "found_equipment":
            return context == "got_equipment"
        elif trigger == "first_recruitment":
            return context == "can_recruit"
        elif trigger == "used_simple_command":
            return stats.get("commands_entered", 0) > 10
        elif trigger == "has_companions":
            return stats.get("companions", 0) > 0
        return False

    def show_tutorial(self, tutorial_id: str) -> Optional[str]:
        """Show a specific tutorial"""
        if tutorial_id in self.tutorials:
            tutorial = self.tutorials[tutorial_id]
            if not tutorial.shown:
                tutorial.shown = True
                self.shown_tutorials.add(tutorial_id)
                return self._format_tutorial(tutorial)
        return None

    def _format_tutorial(self, tutorial: Tutorial) -> str:
        """Format tutorial for display"""
        msg = f"\n{'='*50}\n"
        msg += f"💡 TIP: {tutorial.title}\n"
        msg += f"{'='*50}\n"
        msg += f"{tutorial.message}\n\n"
        msg += "Examples:\n"
        for cmd in tutorial.example_commands:
            msg += f"  > {cmd}\n"
        msg += f"{'='*50}\n"
        return msg

    def discover_feature(self, feature: str):
        """Mark a feature as discovered"""
        if feature not in self.discovered_features:
            self.discovered_features.add(feature)
            # Unlock related tutorial
            for tutorial in self.tutorials.values():
                if tutorial.category.value == feature:
                    return self.show_tutorial(tutorial.id)
        return None

    def get_contextual_examples(self, situation: str) -> List[str]:
        """Get example commands for current situation"""
        examples = {
            "in_combat": [
                "attack [enemy]",
                "flee",
                "use potion",
                "tell [companion] to attack",
            ],
            "with_npc": [
                "talk to [npc]",
                "ask [npc] about [topic]",
                "give [item] to [npc]",
                "recruit [npc]",
            ],
            "with_items": [
                "get [item]",
                "examine [item]",
                "use [item]",
                "put [item] in [container]",
            ],
            "exploring": ["look", "search", "examine [object]", "go [direction]"],
            "with_party": [
                "party",
                "tell [companion] to [action]",
                "gather party",
                "recruit [npc]",
            ],
        }
        return examples.get(situation, [])

    def advance_stage(self):
        """Progress to next tutorial stage"""
        stages = [
            TutorialStage.BEGINNER,
            TutorialStage.INTERMEDIATE,
            TutorialStage.ADVANCED,
            TutorialStage.EXPERT,
        ]
        current_idx = stages.index(self.tutorial_stage)
        if current_idx < len(stages) - 1:
            self.tutorial_stage = stages[current_idx + 1]

    def should_advance_stage(self, stats: Dict[str, int]) -> bool:
        """Check if player should progress to next stage"""
        if self.tutorial_stage == TutorialStage.BEGINNER:
            # Advance after basic exploration
            return (
                stats.get("rooms_visited", 0) >= 5
                and stats.get("items_collected", 0) >= 3
            )
        elif self.tutorial_stage == TutorialStage.INTERMEDIATE:
            # Advance after some combat and interaction
            return (
                stats.get("enemies_defeated", 0) >= 3
                and stats.get("npcs_talked_to", 0) >= 2
            )
        elif self.tutorial_stage == TutorialStage.ADVANCED:
            # Advance to expert after recruiting
            return stats.get("companions_recruited", 0) >= 1
        return False
