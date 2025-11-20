#!/usr/bin/env python3
"""
Adventure Construction Set - Game Engine
A Python implementation of classic text adventure game mechanics
For creating and playing interactive fiction adventures
"""

import json
import random
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Import enhanced parser if available
try:
    from acs.core.parser import NaturalLanguageParser, Companion
    from acs.systems.npc_context import (
        NPCContextManager,
        EmotionalState,
        RelationshipLevel,
    )
    from acs.systems.environment import EnvironmentalSystem, InspectableObject
    from acs.tools.commands import SmartCommandSystem
    from acs.systems.combat import (
        CombatEncounter,
        Combatant,
        CombatTactic,
        StatusEffect,
        CombatPosition,
    )
    from acs.systems.achievements import AchievementSystem
    from acs.systems.journal import AdventureJournal
    from acs.systems.tutorial import ContextualHintSystem
    from acs.tools.modding import ModdingSystem, EventType
    from acs.ui.accessibility import AccessibilitySystem, DifficultyLevel

    ENHANCED_PARSER_AVAILABLE = True
except ImportError:
    ENHANCED_PARSER_AVAILABLE = False
    Companion = None
    NPCContextManager = None
    EnvironmentalSystem = None
    SmartCommandSystem = None
    CombatEncounter = None
    AchievementSystem = None
    AdventureJournal = None
    ContextualHintSystem = None
    ModdingSystem = None
    AccessibilitySystem = None


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    TREASURE = "treasure"
    READABLE = "readable"
    EDIBLE = "edible"
    DRINKABLE = "drinkable"
    CONTAINER = "container"
    NORMAL = "normal"


class MonsterStatus(Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"


@dataclass
class Item:
    """Represents an item in the game world"""

    id: int
    name: str
    description: str
    item_type: ItemType
    weight: int
    value: int
    is_weapon: bool = False
    weapon_type: int = 0  # 1=axe, 2=bow, 3=club, 4=spear, 5=sword
    weapon_dice: int = 1
    weapon_sides: int = 6
    is_armor: bool = False
    armor_value: int = 0
    is_takeable: bool = True
    is_wearable: bool = False
    location: int = 0  # 0=inventory, -1=worn, room_id or monster_id

    def get_damage(self) -> int:
        """Calculate weapon damage"""
        if not self.is_weapon:
            return 0
        return sum(
            random.randint(1, self.weapon_sides) for _ in range(self.weapon_dice)
        )


@dataclass
class Monster:
    """Represents a monster or NPC"""

    id: int
    name: str
    description: str
    room_id: int
    hardiness: int
    agility: int
    friendliness: MonsterStatus
    courage: int
    weapon_id: Optional[int] = None
    armor_worn: int = 0
    gold: int = 0
    is_dead: bool = False
    current_health: Optional[int] = None

    def __post_init__(self):
        if self.current_health is None:
            self.current_health = self.hardiness


@dataclass
class Room:
    """Represents a room/location"""

    id: int
    name: str
    description: str
    exits: Dict[str, int] = field(default_factory=dict)  # direction: room_id
    is_dark: bool = False

    def get_exit(self, direction: str) -> Optional[int]:
        """Get room ID for a given direction"""
        return self.exits.get(direction.lower())


@dataclass
class Player:
    """Player character stats"""

    name: str = "Adventurer"
    hardiness: int = 12
    agility: int = 12
    charisma: int = 12
    weapon_ability: Dict[int, int] = field(
        default_factory=lambda: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5}
    )
    armor_expertise: int = 0
    gold: int = 200
    current_room: int = 1
    current_health: Optional[int] = None
    inventory: List[int] = field(default_factory=list)  # item IDs
    equipped_weapon: Optional[int] = None
    equipped_armor: Optional[int] = None

    def __post_init__(self):
        if self.current_health is None:
            self.current_health = self.hardiness


class AdventureGame:
    """Main game engine for text adventures"""

    def __init__(self, adventure_file: str):
        self.adventure_file = adventure_file
        self.rooms: Dict[int, Room] = {}
        self.items: Dict[int, Item] = {}
        self.monsters: Dict[int, Monster] = {}
        self.player: Player = Player()
        self.companions: List = []  # Party members
        self.turn_count = 0
        self.game_over = False
        self.adventure_title = ""
        self.adventure_intro = ""

        # Initialize enhanced parser if available
        if ENHANCED_PARSER_AVAILABLE:
            self.parser = NaturalLanguageParser()
            self.npc_context_manager = NPCContextManager()
            self.environment = EnvironmentalSystem()
            self.command_system = SmartCommandSystem()
            self.achievements = AchievementSystem()
            self.journal = AdventureJournal()
            self.tutorial = ContextualHintSystem()
            self.modding = ModdingSystem(engine=self)
            self.accessibility = AccessibilitySystem()
            self.use_enhanced_parser = True
        else:
            self.parser = None
            self.npc_context_manager = None
            self.environment = None
            self.command_system = None
            self.achievements = None
            self.journal = None
            self.tutorial = None
            self.modding = None
            self.accessibility = None
            self.use_enhanced_parser = False

        self.effects: List[Dict[str, Any]] = []

    def load_adventure(self):
        """Load adventure data from JSON file"""
        try:
            with open(self.adventure_file, "r") as f:
                data = json.load(f)

            self.adventure_title = data.get("title", "Untitled Adventure")
            self.adventure_intro = data.get("intro", "")

            # Load rooms
            for room_data in data.get("rooms", []):
                room = Room(
                    id=room_data["id"],
                    name=room_data["name"],
                    description=room_data["description"],
                    exits=room_data.get("exits", {}),
                    is_dark=room_data.get("is_dark", False),
                )
                self.rooms[room.id] = room

            # Load items
            for item_data in data.get("items", []):
                item = Item(
                    id=item_data["id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    item_type=ItemType(item_data.get("type", "normal")),
                    weight=item_data.get("weight", 1),
                    value=item_data.get("value", 0),
                    is_weapon=item_data.get("is_weapon", False),
                    weapon_type=item_data.get("weapon_type", 0),
                    weapon_dice=item_data.get("weapon_dice", 1),
                    weapon_sides=item_data.get("weapon_sides", 6),
                    is_armor=item_data.get("is_armor", False),
                    armor_value=item_data.get("armor_value", 0),
                    is_takeable=item_data.get("is_takeable", True),
                    location=item_data.get("location", 0),
                )
                self.items[item.id] = item

            # Load monsters
            for mon_data in data.get("monsters", []):
                monster = Monster(
                    id=mon_data["id"],
                    name=mon_data["name"],
                    description=mon_data["description"],
                    room_id=mon_data.get("room_id", 1),
                    hardiness=mon_data.get("hardiness", 10),
                    agility=mon_data.get("agility", 10),
                    friendliness=MonsterStatus(mon_data.get("friendliness", "neutral")),
                    courage=mon_data.get("courage", 100),
                    weapon_id=mon_data.get("weapon_id"),
                    armor_worn=mon_data.get("armor_worn", 0),
                    gold=mon_data.get("gold", 0),
                )
                self.monsters[monster.id] = monster

            # Load effects (special events)
            self.effects = data.get("effects", [])

            # Set player starting position
            self.player.current_room = data.get("start_room", 1)

            print(f"\n{'=' * 60}")
            print(f"{self.adventure_title:^60}")
            print(f"{'=' * 60}\n")
            if self.adventure_intro:
                print(self.adventure_intro)
                print()

        except FileNotFoundError:
            print(f"Error: Adventure file '{self.adventure_file}' not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in adventure file: {e}")
            sys.exit(1)

    def get_current_room(self) -> Room:
        """Get the room the player is currently in"""
        return self.rooms.get(self.player.current_room)

    def get_items_in_room(self, room_id: int) -> List[Item]:
        """Get all items in a specific room"""
        return [item for item in self.items.values() if item.location == room_id]

    def get_monsters_in_room(self, room_id: int) -> List[Monster]:
        """Get all living monsters in a specific room"""
        return [
            m for m in self.monsters.values() if m.room_id == room_id and not m.is_dead
        ]

    def look(self):
        """Display current room description"""
        room = self.get_current_room()
        print(f"\n{room.name}")
        print("-" * len(room.name))
        print(room.description)

        # Show exits
        if room.exits:
            exits = ", ".join(room.exits.keys())
            print(f"\nObvious exits: {exits}")
        else:
            print("\nNo obvious exits.")

        # Environmental details (time/weather)
        if self.environment:
            self.environment.advance_time()
            room_state = self.environment.get_or_create_room_state(room.id)
            room_state.increment_visit()

            # Show environmental atmosphere occasionally
            if room_state.visited_count == 1:
                print(f"\n{self.environment.get_time_description()}")
                print(self.environment.get_weather_description())

            # Show ambient message occasionally
            ambient = self.environment.get_ambient_message(room.id)
            if ambient:
                print(f"\n{ambient}")

            # Show inspectable objects
            objects = self.environment.get_room_objects(room.id)
            if objects:
                print("\nYou notice:")
                for obj in objects:
                    print(f"  - {obj.short_desc}")

        # Show items
        items = self.get_items_in_room(room.id)
        if items:
            print("\nYou see:")
            for item in items:
                print(f"  - {item.name}")

        # Show monsters
        monsters = self.get_monsters_in_room(room.id)
        if monsters:
            print("\nPresent:")
            for monster in monsters:
                status = (
                    "friendly"
                    if monster.friendliness == MonsterStatus.FRIENDLY
                    else (
                        "hostile"
                        if monster.friendliness == MonsterStatus.HOSTILE
                        else ""
                    )
                )
                print(f"  - {monster.name} {f'({status})' if status else ''}")

    def move(self, direction: str):
        """Move player in a direction"""
        room = self.get_current_room()
        next_room_id = room.get_exit(direction)

        if next_room_id is None:
            print("You can't go that way.")
            return

        self.player.current_room = next_room_id
        self.turn_count += 1

        # Track stats and achievements
        if self.achievements:
            self.achievements.statistics.increment("steps_taken")
            self.achievements.statistics.increment("rooms_visited")
            self.achievements.check_achievements()

        # Log to journal
        if self.journal and self.journal.auto_log_enabled:
            new_room = self.rooms[next_room_id]
            self.journal.log_event(
                title="Room Entered",
                content=f"Entered {new_room.name}",
                room_id=next_room_id,
            )

        # Progress environment time
        if self.environment:
            self.environment.advance_time()

        self.look()

        # Show tutorial hint
        if self.tutorial:
            stats = self.achievements.statistics.to_dict() if self.achievements else {}
            hint = self.tutorial.check_and_show_hint("moved", stats)
            if hint:
                print(self.tutorial._format_tutorial(hint))

    def get_item(self, item_name: str):
        """Pick up an item"""
        room = self.get_current_room()
        items = self.get_items_in_room(room.id)

        # Find matching item
        item = None
        for i in items:
            if item_name.lower() in i.name.lower():
                item = i
                break

        if item is None:
            print(f"You don't see a {item_name} here.")
            return

        if not item.is_takeable:
            print(f"You can't take the {item.name}.")
            return

        item.location = 0  # Move to inventory
        self.player.inventory.append(item.id)
        print(f"You take the {item.name}.")

    def drop_item(self, item_name: str):
        """Drop an item"""
        item = None
        for item_id in self.player.inventory:
            i = self.items[item_id]
            if item_name.lower() in i.name.lower():
                item = i
                break

        if item is None:
            print(f"You don't have a {item_name}.")
            return

        item.location = self.player.current_room
        self.player.inventory.remove(item.id)
        print(f"You drop the {item.name}.")

    def show_inventory(self):
        """Display player inventory"""
        if not self.player.inventory:
            print("\nYou are empty-handed.")
            return

        print("\nYou are carrying:")
        total_weight = 0
        for item_id in self.player.inventory:
            item = self.items[item_id]
            equipped = ""
            if item.id == self.player.equipped_weapon:
                equipped = " (weapon)"
            elif item.id == self.player.equipped_armor:
                equipped = " (armor)"
            print(f"  - {item.name}{equipped}")
            total_weight += item.weight

        print(f"\nTotal weight: {total_weight}")
        print(f"Gold: {self.player.gold}")

    def show_status(self):
        """Display player status"""
        print(f"\n{self.player.name}")
        print("-" * 40)
        print(f"Health: {self.player.current_health}/{self.player.hardiness}")
        print(f"Hardiness: {self.player.hardiness}")
        print(f"Agility: {self.player.agility}")
        print(f"Charisma: {self.player.charisma}")
        print(f"Gold: {self.player.gold}")

        if self.player.equipped_weapon:
            weapon = self.items[self.player.equipped_weapon]
            print(f"Weapon: {weapon.name}")
        if self.player.equipped_armor:
            armor = self.items[self.player.equipped_armor]
            print(f"Armor: {armor.name}")

    def attack(self, target_name: str):
        """Attack a monster"""
        room = self.get_current_room()
        monsters = self.get_monsters_in_room(room.id)

        target = None
        for m in monsters:
            if target_name.lower() in m.name.lower():
                target = m
                break

        if target is None:
            print(f"You don't see a {target_name} here.")
            return

        # Make target hostile
        target.friendliness = MonsterStatus.HOSTILE

        # Player attacks
        damage = 0
        if self.player.equipped_weapon:
            weapon = self.items[self.player.equipped_weapon]
            damage = weapon.get_damage()
        else:
            damage = random.randint(1, 3)  # Bare hands

        print(f"\nYou attack the {target.name}!")
        target.current_health -= damage
        print(f"You hit for {damage} damage!")

        if target.current_health <= 0:
            target.is_dead = True
            print(f"The {target.name} is dead!")
            if target.gold > 0:
                self.player.gold += target.gold
                print(f"You found {target.gold} gold pieces!")
            return

        # Monster counter-attacks
        mon_damage = random.randint(1, 6)
        self.player.current_health -= mon_damage
        print(f"The {target.name} hits you for {mon_damage} damage!")

        if self.player.current_health <= 0:
            print("\nYou have died!")
            self.game_over = True

    # NPC Interaction & Context Methods
    def talk_to_npc(self, npc_name: str, topic: str = None):
        """Enhanced NPC interaction with memory and emotions"""
        room = self.get_current_room()
        monsters = self.get_monsters_in_room(room.id)

        # Find the NPC
        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if npc is None:
            print(f"You don't see {npc_name} here.")
            return

        # Get or create NPC context
        if self.npc_context_manager:
            context = self.npc_context_manager.get_or_create_context(npc.id, npc.name)

            # Show greeting based on relationship
            print(f"\n{context.get_greeting()}")

            # Record the conversation
            if topic:
                context.memory.add_topic(topic)
                print(f'You ask about "{topic}".')

                # Check if topic has been discussed before
                if context.memory.has_discussed(topic):
                    print(
                        f"{npc.name} says {context.get_dialogue_modifier()}, "
                        f'"We\'ve discussed this before..."'
                    )
                else:
                    print(f"{npc.name} responds {context.get_dialogue_modifier()}.")

            context.memory.increment_conversation()

            # Show relationship status for trusted+ NPCs
            if context.relationship.value >= 2:
                print(
                    f"[{npc.name} considers you a "
                    f"{context.relationship.name.lower()}]"
                )
        else:
            # Fallback for simple interaction
            print(f"You talk to {npc.name}.")
            if npc.friendliness == MonsterStatus.FRIENDLY:
                print(f"{npc.name} seems friendly.")
            elif npc.friendliness == MonsterStatus.HOSTILE:
                print(f"{npc.name} looks angry!")

    def examine_npc(self, npc_name: str):
        """Examine an NPC to learn about them"""
        room = self.get_current_room()
        monsters = self.get_monsters_in_room(room.id)

        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if npc is None:
            print(f"You don't see {npc_name} here.")
            return

        print(f"\n{npc.description}")

        # Show context-aware details
        if self.npc_context_manager:
            context = self.npc_context_manager.get_context(npc.id)
            if context:
                print(f"{npc.name} appears {context.current_mood}.")

                # Show personality if familiar
                if context.memory.times_talked >= 3:
                    if context.personality_traits:
                        traits = ", ".join(context.personality_traits)
                        print(f"They seem {traits}.")

    def examine_object(self, object_name: str):
        """Examine an environmental object"""
        if not self.environment:
            print(f"You examine the {object_name} closely...")
            return

        room = self.get_current_room()
        obj = self.environment.find_object_by_keyword(room.id, object_name)

        if obj:
            print(f"\n{obj.long_desc}")

            # Reveal item if object contains one
            if obj.contains_item_id:
                item = self.items.get(obj.contains_item_id)
                if item:
                    print(f"\nYou found: {item.name}!")
                    item.location = room.id
        else:
            print(f"You don't see anything special about {object_name}.")

    def search_area(self):
        """Search current area for hidden objects"""
        if not self.environment:
            print("You search the area carefully...")
            return

        room = self.get_current_room()
        found = self.environment.search_room(room.id)

        if found:
            print("\nYour careful search reveals:")
            for obj in found:
                print(f"  - {obj.short_desc}")
        else:
            print("You search carefully but find nothing hidden.")

    # Party/Companion Management Methods
    def recruit_companion(self, npc_name: str):
        """Recruit an NPC as a companion"""
        if not ENHANCED_PARSER_AVAILABLE:
            print("Companion system not available.")
            return

        room = self.get_current_room()
        monsters = self.get_monsters_in_room(room.id)

        # Find NPC
        npc = None
        for m in monsters:
            if npc_name.lower() in m.name.lower():
                npc = m
                break

        if not npc:
            print(f"You don't see {npc_name} here.")
            return

        # Check if NPC is friendly
        if npc.friendliness != MonsterStatus.FRIENDLY:
            print(f"{npc.name} doesn't seem interested in joining you.")
            return

        # Check party size
        if len(self.companions) >= 3:
            print("Your party is full! (Maximum 3 companions)")
            return

        # Determine role
        role = "fighter"
        if npc.agility > npc.hardiness:
            role = "rogue"

        # Create companion
        companion = Companion(npc.id, npc.name, role)
        companion.current_health = npc.current_health
        companion.max_health = npc.hardiness

        self.companions.append(companion)
        print(f"\n{npc.name} joins your party as a {role}!")
        npc.room_id = -999

    def show_party(self):
        """Display party status"""
        if not self.companions:
            print("\nYou are traveling alone.")
            return

        print("\n" + "=" * 50)
        print("YOUR PARTY")
        print("=" * 50)
        for companion in self.companions:
            alive = "ALIVE" if companion.is_alive() else "DEAD"
            status_info = ""
            if hasattr(companion, "is_waiting") and companion.is_waiting:
                status_info = " (WAITING)"
            print(f"\n{companion.name} - {companion.role} " f"({alive}){status_info}")
            print(f"  HP: {companion.current_health}/{companion.max_health}")
            print(f"  Loyalty: {companion.loyalty}/100")
            if hasattr(companion, "stance"):
                print(f"  Stance: {companion.stance.value}")
        print("=" * 50)

    def party_command(self, companion_name: str, order: str):
        """Give orders to a specific companion"""
        if not ENHANCED_PARSER_AVAILABLE:
            print("Party commands not available.")
            return

        # Find companion
        companion = None
        for c in self.companions:
            if companion_name.lower() in c.name.lower():
                companion = c
                break

        if not companion:
            print(f"{companion_name} is not in your party.")
            return

        order = order.lower().strip()

        # Handle different orders
        if "wait" in order or "stay" in order:
            companion.tell_to_wait(self.player.current_room)
            print(f"{companion.name} will wait here.")
        elif "follow" in order or "come" in order:
            companion.tell_to_follow()
            print(f"{companion.name} resumes following you.")
        elif "aggressive" in order or "attack" in order:
            from acs_parser import CompanionStance

            companion.set_stance(CompanionStance.AGGRESSIVE)
            print(f"{companion.name} will fight aggressively.")
        elif "defensive" in order or "defend" in order:
            from acs_parser import CompanionStance

            companion.set_stance(CompanionStance.DEFENSIVE)
            print(f"{companion.name} will focus on defense.")
        elif "support" in order or "help" in order:
            from acs_parser import CompanionStance

            companion.set_stance(CompanionStance.SUPPORT)
            print(f"{companion.name} will support the party.")
        elif "passive" in order or "rest" in order:
            from acs_parser import CompanionStance

            companion.set_stance(CompanionStance.PASSIVE)
            print(f"{companion.name} will avoid combat.")
        else:
            print(f"You tell {companion.name}: {order}")
            print(f"{companion.name} nods in understanding.")

    def gather_party(self):
        """Bring all waiting companions to current location"""
        if not ENHANCED_PARSER_AVAILABLE:
            return

        gathered = []
        for companion in self.companions:
            if hasattr(companion, "is_waiting") and companion.is_waiting:
                companion.tell_to_follow()
                gathered.append(companion.name)

        if gathered:
            names = ", ".join(gathered)
            print(f"{names} rejoin(s) your party.")
        else:
            print("All companions are already following you.")

    def process_command(self, command: str):
        """Process a player command"""
        # Process with smart command system if available
        if self.command_system:
            # Fix typos and process
            command = self.command_system.process_input(command)
            # Add to history
            self.command_system.add_to_history(command)

        # Try enhanced parser first
        if self.use_enhanced_parser and self.parser:
            parsed = self.parser.parse_command(command)
            action = parsed.get("action")

            if action == "quit":
                print("\nThanks for playing!")
                self.game_over = True
                return
            elif action == "help":
                self.show_help()
                return
            elif action == "move":
                self.move(parsed.get("direction", ""))
                return
            elif action == "look":
                if parsed.get("target"):
                    print(f"You examine the {parsed['target']}...")
                    # Could add detailed examine here
                else:
                    self.look()
                return
            elif action == "get":
                target = parsed.get("target", parsed.get("object", ""))
                if target:
                    self.get_item(target)
                else:
                    print("Get what?")
                return
            elif action == "drop":
                target = parsed.get("target", parsed.get("object", ""))
                if target:
                    self.drop_item(target)
                else:
                    print("Drop what?")
                return
            elif action == "attack":
                target = parsed.get("target", "")
                if target:
                    self.attack(target)
                else:
                    print("Attack what?")
                return
            elif action == "inventory":
                self.show_inventory()
                return
            elif action == "status":
                self.show_status()
                return
            elif action == "party":
                self.show_party()
                return
            elif action == "recruit":
                target = parsed.get("target", "")
                if target:
                    self.recruit_companion(target)
                else:
                    print("Recruit who?")
                return
            elif action == "party_order":
                companion = parsed.get("companion", "")
                order = parsed.get("order", "")
                if companion and order:
                    self.party_command(companion, order)
                else:
                    print("Tell who to do what?")
                return
            elif action == "gather":
                self.gather_party()
                return
            elif action == "eat" or action == "drink":
                target = parsed.get("target", "")
                if target:
                    # Try to find the item in inventory
                    item = None
                    for i in self.player.inventory:
                        if target.lower() in i.name.lower():
                            item = i
                            break

                    if item:
                        # Check if it's consumable
                        consumable = hasattr(item, "consumable") and item.consumable
                        if consumable:
                            print(f"You {action} the {item.name}.")
                            # Apply any effects (healing, etc)
                            if hasattr(item, "heal_amount") and item.heal_amount > 0:
                                old_health = self.player.health
                                new_health = min(
                                    self.player.max_health,
                                    old_health + item.heal_amount,
                                )
                                self.player.health = new_health
                                heal_msg = (
                                    f"You feel refreshed! "
                                    f"Health restored by "
                                    f"{item.heal_amount}."
                                )
                                print(heal_msg)
                            self.player.inventory.remove(item)
                        else:
                            print(f"You can't {action} that.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "trade":
                target = parsed.get("target", "")
                if target:
                    # Find NPC to trade with
                    room = self.get_current_room()
                    monsters = self.get_monsters_in_room(room.id)
                    npc = None
                    for m in monsters:
                        if target.lower() in m.name.lower():
                            npc = m
                            break

                    if npc:
                        # Check if NPC is a merchant
                        is_merchant = hasattr(npc, "is_merchant") and npc.is_merchant
                        if is_merchant:
                            print(f"You begin trading with {npc.name}.")
                            # Show merchant inventory if available
                            if hasattr(npc, "inventory") and npc.inventory:
                                print("\nAvailable items:")
                                for item in npc.inventory:
                                    price = item.value if hasattr(item, "value") else 10
                                    print(f"  - {item.name} ({price} gold)")
                                print("\nUse 'buy [item]' or 'sell [item]'")
                            else:
                                print(f"{npc.name} has nothing to trade.")
                        else:
                            print(f"{npc.name} doesn't want to trade.")
                    else:
                        print(f"You don't see any {target} here.")
                else:
                    print("Trade with whom?")
                return
            elif action == "buy":
                target = parsed.get("target", "")
                if target:
                    # Find merchant NPC in current room
                    room = self.get_current_room()
                    monsters = self.get_monsters_in_room(room.id)
                    merchant = None
                    for m in monsters:
                        is_merch = hasattr(m, "is_merchant") and m.is_merchant
                        if is_merch:
                            merchant = m
                            break

                    if merchant:
                        # Find item in merchant's inventory
                        item = None
                        if hasattr(merchant, "inventory"):
                            for i in merchant.inventory:
                                if target.lower() in i.name.lower():
                                    item = i
                                    break

                        if item:
                            price = item.value if hasattr(item, "value") else 10
                            player_gold = (
                                self.player.gold if hasattr(self.player, "gold") else 0
                            )
                            if player_gold >= price:
                                self.player.gold -= price
                                self.player.inventory.append(item)
                                merchant.inventory.remove(item)
                                print(f"You bought {item.name} for " f"{price} gold.")
                            else:
                                print(f"You need {price} gold to buy that.")
                        else:
                            print(f"The merchant doesn't have any {target}.")
                    else:
                        print("There's no merchant here.")
                else:
                    print("Buy what?")
                return
            elif action == "sell":
                target = parsed.get("target", "")
                if target:
                    # Find merchant NPC in current room
                    room = self.get_current_room()
                    monsters = self.get_monsters_in_room(room.id)
                    merchant = None
                    for m in monsters:
                        is_merch = hasattr(m, "is_merchant") and m.is_merchant
                        if is_merch:
                            merchant = m
                            break

                    if merchant:
                        # Find item in player's inventory
                        item = None
                        for i in self.player.inventory:
                            if target.lower() in i.name.lower():
                                item = i
                                break

                        if item:
                            price = item.value if hasattr(item, "value") else 5
                            sell_price = price // 2
                            if not hasattr(self.player, "gold"):
                                self.player.gold = 0
                            self.player.gold += sell_price
                            self.player.inventory.remove(item)
                            if hasattr(merchant, "inventory"):
                                merchant.inventory.append(item)
                            print(f"You sold {item.name} for " f"{sell_price} gold.")
                        else:
                            print(f"You don't have any {target}.")
                    else:
                        print("There's no merchant here.")
                else:
                    print("Sell what?")
                return
            elif action == "use":
                target = parsed.get("target", "")
                if target:
                    # Find item in inventory
                    item = None
                    for i in self.player.inventory:
                        if target.lower() in i.name.lower():
                            item = i
                            break

                    if item:
                        # Check for usable attribute
                        if hasattr(item, "usable") and item.usable:
                            print(f"You use the {item.name}.")
                            # Apply effects if any
                            if hasattr(item, "on_use"):
                                item.on_use(self.player, self)
                        else:
                            print(f"You can't use the {item.name}.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print("Use what?")
                return
            elif action == "open" or action == "close":
                target = parsed.get("target", "")
                if target:
                    room = self.get_current_room()
                    # Check if target is in room
                    found = False
                    if hasattr(room, "features"):
                        for feature in room.features:
                            if target.lower() in feature.lower():
                                found = True
                                state = "opened" if action == "open" else "closed"
                                print(f"You {action} the {target}.")
                                # Could store state changes here
                                break

                    if not found:
                        print(f"You don't see any {target} to {action}.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "equip" or action == "unequip":
                target = parsed.get("target", "")
                if target:
                    item = None
                    if action == "equip":
                        # Find in inventory
                        for i in self.player.inventory:
                            if target.lower() in i.name.lower():
                                item = i
                                break

                        if item:
                            equippable = hasattr(item, "equippable") and item.equippable
                            if equippable:
                                # Add to equipped set
                                if not hasattr(self.player, "equipped"):
                                    self.player.equipped = set()
                                self.player.equipped.add(item)
                                print(f"You equip the {item.name}.")
                            else:
                                print(f"You can't equip the {item.name}.")
                        else:
                            print(f"You don't have any {target}.")
                    else:  # unequip
                        if hasattr(self.player, "equipped"):
                            for i in self.player.equipped:
                                if target.lower() in i.name.lower():
                                    item = i
                                    break

                            if item:
                                self.player.equipped.remove(item)
                                print(f"You unequip the {item.name}.")
                            else:
                                print(f"You don't have {target} equipped.")
                        else:
                            print("You don't have anything equipped.")
                else:
                    print(f"{action.capitalize()} what?")
                return
            elif action == "flee":
                # Try to escape from combat or dangerous situation
                if hasattr(self, "combat") and self.combat.in_combat:
                    print("You attempt to flee from combat!")
                    # Simple flee logic
                    import random

                    if random.random() > 0.5:
                        self.combat.in_combat = False
                        print("You successfully escaped!")
                    else:
                        print("You couldn't get away!")
                else:
                    # Not in combat, just move to random exit
                    room = self.get_current_room()
                    if room.exits:
                        import random

                        direction = random.choice(list(room.exits.keys()))
                        print(f"You flee {direction}!")
                        self.move(direction)
                    else:
                        print("There's nowhere to flee!")
                return
            elif action == "give":
                target = parsed.get("target", "")
                recipient = parsed.get("recipient", "")
                if target and recipient:
                    # Find item in inventory
                    item = None
                    for i in self.player.inventory:
                        if target.lower() in i.name.lower():
                            item = i
                            break

                    if item:
                        # Find NPC
                        room = self.get_current_room()
                        monsters = self.get_monsters_in_room(room.id)
                        npc = None
                        for m in monsters:
                            if recipient.lower() in m.name.lower():
                                npc = m
                                break

                        if npc:
                            self.player.inventory.remove(item)
                            if hasattr(npc, "inventory"):
                                npc.inventory.append(item)
                            print(f"You give the {item.name} to {npc.name}.")
                        else:
                            print(f"You don't see any {recipient} here.")
                    else:
                        print(f"You don't have any {target}.")
                else:
                    print("Give what to whom?")
                return
            elif action == "quests":
                # Show active quests
                if hasattr(self.player, "quests") and self.player.quests:
                    print("\n=== Active Quests ===")
                    for quest in self.player.quests:
                        status = "Complete" if quest.completed else "Active"
                        print(f"[{status}] {quest.name}")
                        print(f"  {quest.description}")
                else:
                    print("You have no active quests.")
                return
            elif action == "dismiss":
                target = parsed.get("target", "")
                if target:
                    if hasattr(self.player, "party"):
                        companion = None
                        for c in self.player.party:
                            if target.lower() in c.name.lower():
                                companion = c
                                break

                        if companion:
                            self.player.party.remove(companion)
                            print(f"{companion.name} has left your party.")
                        else:
                            print(f"{target} is not in your party.")
                    else:
                        print("You don't have any companions.")
                else:
                    print("Dismiss whom?")
                return
            elif action == "examine":
                target = parsed.get("target", "")
                if target:
                    # Check if examining an NPC
                    room = self.get_current_room()
                    monsters = self.get_monsters_in_room(room.id)
                    is_npc = any(target.lower() in m.name.lower() for m in monsters)
                    if is_npc:
                        self.examine_npc(target)
                    else:
                        # Examine environmental object or item
                        self.examine_object(target)
                else:
                    print("Examine what?")
                return
            elif action == "search":
                self.search_area()
                return
            elif action == "talk":
                target = parsed.get("target", "")
                topic = parsed.get("topic", "")
                if target:
                    self.talk_to_npc(target, topic)
                else:
                    print("Talk to whom?")
                return
            elif action == "question":
                # Handle questions naturally
                q_text = parsed.get("text", "")
                if "where" in q_text.lower():
                    self.look()
                elif "what" in q_text.lower() and "carry" in q_text.lower():
                    self.show_inventory()
                elif "who" in q_text.lower():
                    monsters = self.get_monsters_in_room(self.player.current_room)
                    if monsters:
                        print("You see:")
                        for m in monsters:
                            print(f"  - {m.name}")
                    else:
                        print("No one else is here.")
                else:
                    print("I'm not sure how to answer that.")
                return

        # Fall back to simple parser
        parts = command.lower().strip().split()
        if not parts:
            return

        cmd = parts[0]
        args = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Movement commands
        if cmd in ["n", "north"]:
            self.move("north")
        elif cmd in ["s", "south"]:
            self.move("south")
        elif cmd in ["e", "east"]:
            self.move("east")
        elif cmd in ["w", "west"]:
            self.move("west")
        elif cmd in ["u", "up"]:
            self.move("up")
        elif cmd in ["d", "down"]:
            self.move("down")

        # Action commands
        elif cmd in ["l", "look"]:
            self.look()
        elif cmd in ["i", "inventory"]:
            self.show_inventory()
        elif cmd in ["status", "stats"]:
            self.show_status()
        elif cmd in ["party"]:
            self.show_party()
        elif cmd in ["recruit", "invite"]:
            if args:
                self.recruit_companion(args)
            else:
                print("Recruit who?")
        elif cmd in ["get", "take"]:
            if args:
                self.get_item(args)
            else:
                print("Get what?")
        elif cmd in ["drop"]:
            if args:
                self.drop_item(args)
            else:
                print("Drop what?")
        elif cmd in ["attack", "kill", "fight"]:
            if args:
                self.attack(args)
            else:
                print("Attack what?")
        elif cmd in ["quit", "exit", "q"]:
            print("\nThanks for playing!")
            self.game_over = True
        elif cmd in ["help", "h", "?"]:
            self.show_help()
        elif cmd in ["achievements"]:
            if self.achievements:
                print("\n" + self.achievements.get_progress_summary())
            else:
                print("Achievements not available.")
        elif cmd in ["journal", "notes"]:
            if self.journal:
                entries = self.journal.get_recent_entries(10)
                print("\n=== Recent Journal Entries ===")
                for entry in entries:
                    print(f"\n[{entry.timestamp}] {entry.title}")
                    print(f"  {entry.content}")
            else:
                print("Journal not available.")
        elif cmd in ["settings"]:
            if self.accessibility:
                print("\n=== Game Settings ===")
                print(f"Difficulty: {self.accessibility.difficulty.level.value}")
                print(f"Text Size: {self.accessibility.display.text_size.value}")
                print(
                    f"Colors: {'Enabled' if self.accessibility.display.use_colors else 'Disabled'}"
                )
            else:
                print("Settings not available.")
        else:
            print(f"I don't understand '{command}'. Type 'help' for commands.")

    def show_help(self):
        """Display help text"""
        if self.use_enhanced_parser and self.parser:
            print(self.parser.get_help_text())
        else:
            print("\n" + "=" * 60)
            print("ADVENTURE COMMANDS")
            print("=" * 60)
            print("\nMovement:")
            print("  n, north, s, south, e, east, w, west, u, up, d, down")
            print("\nActions:")
            print("  look (l)        - Look around")
            print("  get/take <item> - Pick up an item")
            print("  drop <item>     - Drop an item")
            print("  attack <target> - Attack a monster")
            print("\nParty:")
            print("  party           - View your companions")
            print("  recruit <npc>   - Invite NPC to join party")
            print("\nInfo:")
            print("  inventory (i)   - Show what you're carrying")
            print("  status          - Show your character stats")
            print("  help (h, ?)     - Show this help")
            print("\nOther:")
            print("  quit (q)        - Exit the game")
            print("=" * 60 + "\n")

    def run(self):
        """Main game loop"""
        self.load_adventure()
        self.look()

        while not self.game_over:
            try:
                command = input("\n> ").strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\n\nThanks for playing!")
                break
            except EOFError:
                break


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Usage: adventure_engine.py <adventure_file.json>")
        sys.exit(1)

    game = AdventureGame(sys.argv[1])
    game.run()


if __name__ == "__main__":
    main()
