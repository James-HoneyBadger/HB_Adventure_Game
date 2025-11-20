#!/usr/bin/env python3
"""
Adventure Construction Set - Enhanced Combat System
Provides tactical combat, status effects, and intelligent enemy AI
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class CombatPosition(Enum):
    """Tactical positioning in combat"""

    FRONT = "front"
    BACK = "back"


class StatusEffect(Enum):
    """Combat status effects"""

    POISONED = "poisoned"
    STUNNED = "stunned"
    BLESSED = "blessed"
    CURSED = "cursed"
    BURNING = "burning"
    FROZEN = "frozen"
    STRENGTHENED = "strengthened"
    WEAKENED = "weakened"
    DEFENDING = "defending"
    BERSERKING = "berserking"


class CombatTactic(Enum):
    """Enemy AI tactics"""

    AGGRESSIVE = "aggressive"  # Attack strongest target
    DEFENSIVE = "defensive"  # Focus on survival
    OPPORTUNISTIC = "opportunistic"  # Attack weakest
    SUPPORT = "support"  # Help allies
    FLEE_WHEN_HURT = "flee_when_hurt"  # Run at low HP


@dataclass
class ActiveEffect:
    """An active status effect on a combatant"""

    effect_type: StatusEffect
    duration: int  # Turns remaining
    power: int = 1  # Effect strength
    source: str = "unknown"

    def tick(self) -> bool:
        """Reduce duration, return True if still active"""
        self.duration -= 1
        return self.duration > 0


@dataclass
class CombatAction:
    """Records a combat action for narration"""

    actor: str
    action_type: str  # attack, defend, cast, item, flee
    target: Optional[str] = None
    damage: int = 0
    effect: Optional[str] = None
    critical: bool = False
    dodged: bool = False
    blocked: bool = False


class Combatant:
    """Represents a participant in combat"""

    def __init__(
        self,
        name: str,
        health: int,
        max_health: int,
        attack: int,
        defense: int,
        agility: int,
    ):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.position = CombatPosition.FRONT
        self.active_effects: List[ActiveEffect] = []
        self.is_defending = False
        self.combo_count = 0

    def add_effect(self, effect: StatusEffect, duration: int, power: int = 1):
        """Add status effect"""
        # Check if effect already exists
        for existing in self.active_effects:
            if existing.effect_type == effect:
                # Refresh duration if new is longer
                existing.duration = max(existing.duration, duration)
                existing.power = max(existing.power, power)
                return

        # Add new effect
        self.active_effects.append(ActiveEffect(effect, duration, power))

    def remove_effect(self, effect: StatusEffect):
        """Remove status effect"""
        self.active_effects = [
            e for e in self.active_effects if e.effect_type != effect
        ]

    def has_effect(self, effect: StatusEffect) -> bool:
        """Check if combatant has effect"""
        return any(e.effect_type == effect for e in self.active_effects)

    def tick_effects(self) -> List[str]:
        """Process status effects, return messages"""
        messages = []

        for effect in list(self.active_effects):
            # Apply effect
            if effect.effect_type == StatusEffect.POISONED:
                damage = effect.power
                self.health -= damage
                messages.append(f"{self.name} takes {damage} poison damage!")
            elif effect.effect_type == StatusEffect.BURNING:
                damage = effect.power * 2
                self.health -= damage
                messages.append(f"{self.name} burns for {damage} damage!")
            elif effect.effect_type == StatusEffect.FROZEN:
                messages.append(f"{self.name} is frozen solid!")

            # Tick down duration
            if not effect.tick():
                self.active_effects.remove(effect)
                messages.append(
                    f"{self.name} is no longer " f"{effect.effect_type.value}!"
                )

        return messages

    def get_attack_bonus(self) -> int:
        """Calculate total attack bonus from effects"""
        bonus = 0
        if self.has_effect(StatusEffect.STRENGTHENED):
            bonus += 5
        if self.has_effect(StatusEffect.WEAKENED):
            bonus -= 5
        if self.has_effect(StatusEffect.BLESSED):
            bonus += 3
        if self.has_effect(StatusEffect.CURSED):
            bonus -= 3
        if self.has_effect(StatusEffect.BERSERKING):
            bonus += 10
        return bonus

    def get_defense_bonus(self) -> int:
        """Calculate total defense bonus from effects"""
        bonus = 0
        if self.is_defending:
            bonus += 5
        if self.has_effect(StatusEffect.DEFENDING):
            bonus += 3
        if self.has_effect(StatusEffect.BLESSED):
            bonus += 2
        if self.has_effect(StatusEffect.CURSED):
            bonus -= 2
        if self.position == CombatPosition.BACK:
            bonus += 2
        return bonus

    def can_act(self) -> bool:
        """Check if combatant can take actions"""
        if self.has_effect(StatusEffect.STUNNED):
            return False
        if self.has_effect(StatusEffect.FROZEN):
            return False
        return True


class EnemyAI:
    """Intelligent enemy combat decisions"""

    def __init__(self, tactic: CombatTactic = CombatTactic.AGGRESSIVE):
        self.tactic = tactic
        self.flee_threshold = 0.3  # Flee at 30% health

    def choose_target(
        self, enemies: List[Combatant], self_combatant: Combatant
    ) -> Optional[Combatant]:
        """Choose target based on AI tactic"""
        alive_enemies = [e for e in enemies if e.health > 0]
        if not alive_enemies:
            return None

        if self.tactic == CombatTactic.AGGRESSIVE:
            # Attack highest health target
            return max(alive_enemies, key=lambda e: e.health)
        elif self.tactic == CombatTactic.OPPORTUNISTIC:
            # Attack weakest target
            return min(alive_enemies, key=lambda e: e.health)
        elif self.tactic == CombatTactic.DEFENSIVE:
            # Attack whoever attacked last (if tracked)
            # For now, random front-line target
            front_line = [
                e for e in alive_enemies if e.position == CombatPosition.FRONT
            ]
            return random.choice(front_line if front_line else alive_enemies)
        else:
            return random.choice(alive_enemies)

    def should_flee(self, combatant: Combatant) -> bool:
        """Check if AI should flee"""
        if self.tactic != CombatTactic.FLEE_WHEN_HURT:
            return False
        health_percent = combatant.health / combatant.max_health
        return health_percent < self.flee_threshold

    def choose_action(
        self, combatant: Combatant, allies: List[Combatant], enemies: List[Combatant]
    ) -> str:
        """Decide what action to take"""
        # Check if should flee
        if self.should_flee(combatant):
            return "flee"

        # Support tactic - heal if ally is hurt
        if self.tactic == CombatTactic.SUPPORT:
            hurt_allies = [a for a in allies if a.health < a.max_health * 0.5]
            if hurt_allies:
                return "heal"

        # Defensive - defend if low health
        if (
            self.tactic == CombatTactic.DEFENSIVE
            and combatant.health < combatant.max_health * 0.4
        ):
            return "defend"

        # Default to attack
        return "attack"


class CombatNarrator:
    """Generates dynamic combat descriptions"""

    def __init__(self):
        self.attack_verbs = [
            "strikes",
            "hits",
            "slashes",
            "pounds",
            "smashes",
            "cuts",
            "stabs",
            "batters",
            "whacks",
        ]
        self.miss_verbs = [
            "misses",
            "swings wildly at",
            "fails to hit",
            "attacks unsuccessfully",
        ]
        self.critical_phrases = [
            "lands a devastating blow on",
            "strikes a critical hit against",
            "finds a weak spot in",
            "delivers a crushing attack to",
        ]

    def narrate_attack(self, action: CombatAction) -> str:
        """Generate attack narration"""
        if action.critical:
            verb = random.choice(self.critical_phrases)
            return (
                f"{action.actor} {verb} {action.target} "
                f"for {action.damage} damage! *CRITICAL HIT*"
            )
        elif action.dodged:
            return f"{action.target} dodges {action.actor}'s attack!"
        elif action.blocked:
            return f"{action.target} blocks {action.actor}'s attack!"
        elif action.damage > 0:
            verb = random.choice(self.attack_verbs)
            return (
                f"{action.actor} {verb} {action.target} " f"for {action.damage} damage!"
            )
        else:
            verb = random.choice(self.miss_verbs)
            return f"{action.actor} {verb} {action.target}!"

    def narrate_combo(self, attacker: str, combo_count: int) -> str:
        """Narrate combo attacks"""
        if combo_count == 2:
            return f"{attacker} chains attacks together!"
        elif combo_count == 3:
            return f"{attacker} unleashes a flurry of strikes!"
        elif combo_count >= 4:
            return f"{attacker} is on an unstoppable rampage!"
        return ""


class CombatEncounter:
    """Manages a complete combat encounter"""

    def __init__(self):
        self.player_side: List[Combatant] = []
        self.enemy_side: List[Combatant] = []
        self.turn_count = 0
        self.combat_log: List[CombatAction] = []
        self.narrator = CombatNarrator()
        self.enemy_ai: Dict[str, EnemyAI] = {}

    def add_player_combatant(self, combatant: Combatant):
        """Add player or companion to combat"""
        self.player_side.append(combatant)

    def add_enemy_combatant(
        self, combatant: Combatant, ai_tactic: CombatTactic = CombatTactic.AGGRESSIVE
    ):
        """Add enemy to combat"""
        self.enemy_side.append(combatant)
        self.enemy_ai[combatant.name] = EnemyAI(ai_tactic)

    def resolve_attack(self, attacker: Combatant, defender: Combatant) -> CombatAction:
        """Resolve an attack between combatants"""
        action = CombatAction(
            actor=attacker.name, action_type="attack", target=defender.name
        )

        # Check if attacker can act
        if not attacker.can_act():
            action.damage = 0
            return action

        # Calculate hit chance
        hit_chance = 70 + (attacker.agility - defender.agility) * 2
        hit_roll = random.randint(1, 100)

        # Check for critical
        critical_chance = 5 + attacker.combo_count * 2
        if hit_roll <= critical_chance:
            action.critical = True

        # Check if hit
        if hit_roll > hit_chance:
            action.dodged = True
            attacker.combo_count = 0
            return action

        # Calculate damage
        base_damage = random.randint(1, 6) + attacker.attack
        base_damage += attacker.get_attack_bonus()

        if action.critical:
            base_damage *= 2
            attacker.combo_count += 1
        else:
            attacker.combo_count += 1

        # Apply defense
        defense = defender.defense + defender.get_defense_bonus()
        final_damage = max(1, base_damage - defense)

        # Check if blocked
        if defender.is_defending:
            block_roll = random.randint(1, 100)
            if block_roll <= 50:
                action.blocked = True
                final_damage = final_damage // 2

        action.damage = final_damage
        defender.health -= final_damage

        return action

    def process_turn(self) -> List[str]:
        """Process one combat turn"""
        messages = []
        self.turn_count += 1

        # Process status effects
        for combatant in self.player_side + self.enemy_side:
            effect_msgs = combatant.tick_effects()
            messages.extend(effect_msgs)

        # Get all combatants sorted by agility
        all_combatants = [(c, "player") for c in self.player_side if c.health > 0] + [
            (c, "enemy") for c in self.enemy_side if c.health > 0
        ]
        all_combatants.sort(key=lambda x: x[0].agility, reverse=True)

        # Each combatant acts
        for combatant, side in all_combatants:
            if combatant.health <= 0:
                continue

            # Reset defending status
            combatant.is_defending = False

            if side == "enemy":
                # AI decision
                ai = self.enemy_ai.get(combatant.name)
                if ai:
                    action = ai.choose_action(
                        combatant, self.enemy_side, self.player_side
                    )
                    if action == "flee":
                        messages.append(f"{combatant.name} flees!")
                        combatant.health = 0
                        continue
                    elif action == "defend":
                        combatant.is_defending = True
                        messages.append(f"{combatant.name} takes a defensive stance!")
                        continue

                # Choose target and attack
                target = ai.choose_target(self.player_side, combatant)
                if target:
                    attack_action = self.resolve_attack(combatant, target)
                    messages.append(self.narrator.narrate_attack(attack_action))

                    if combatant.combo_count > 1:
                        combo_msg = self.narrator.narrate_combo(
                            combatant.name, combatant.combo_count
                        )
                        if combo_msg:
                            messages.append(combo_msg)

        return messages

    def is_combat_over(self) -> tuple:
        """Check if combat is over, return (over, player_won)"""
        players_alive = any(c.health > 0 for c in self.player_side)
        enemies_alive = any(c.health > 0 for c in self.enemy_side)

        if not players_alive:
            return (True, False)
        if not enemies_alive:
            return (True, True)
        return (False, False)
