#!/usr/bin/env python3
"""
Adventure Construction Set - Enhanced Natural Language Parser
Provides improved command parsing with better sentence understanding
and support for party/companion system
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum


class NaturalLanguageParser:
    """Enhanced parser that understands natural language commands"""

    def __init__(self):
        # Verb synonyms for common actions
        self.verb_map = {
            # Movement
            "go": ["move", "walk", "run", "travel", "head", "proceed"],
            "enter": ["step into"],  # Removed "go in", "go into"
            "exit": ["depart"],  # Removed "go out"
            # Looking/Examining
            "look": [
                "l",
                "examine",
                "inspect",
                "check",
                "view",
                "observe",
                "see",
                "study",
                "peer at",
                "gaze at",
            ],
            "read": ["peruse", "scan"],
            "search": ["seek", "hunt for", "look for", "find"],
            # Taking/Dropping
            "get": [
                "take",
                "grab",
                "pick up",
                "acquire",
                "obtain",
                "collect",
                "lift",
                "snatch",
                "gather",
            ],
            "drop": ["put down", "leave", "discard", "release", "abandon"],
            "put": ["place", "set", "insert", "stow"],
            # Inventory
            "inventory": [
                "i",
                "inv",
                "items",
                "possessions",
                "belongings",
                "what am i carrying",
                "what do i have",
            ],
            # Equipment
            "equip": ["wear", "wield", "don", "put on", "arm"],
            "unequip": ["remove", "take off", "doff", "unwield"],
            # Combat
            "attack": [
                "fight",
                "hit",
                "strike",
                "kill",
                "slay",
                "battle",
                "combat",
                "assault",
                "hurt",
                "punch",
                "kick",
            ],
            "flee": ["run away", "escape", "retreat", "run"],
            # Interaction
            "talk": ["speak", "chat", "converse", "say", "ask"],  # Removed "tell"
            "give": ["offer", "hand", "present"],
            "trade": ["barter", "exchange", "swap", "buy", "sell"],
            # Using items
            "use": ["utilize", "employ", "activate", "apply"],
            "open": ["unlock", "unfasten"],
            "close": ["shut", "lock", "fasten"],
            "drink": ["sip", "quaff", "gulp"],
            "eat": ["consume", "devour", "munch"],
            # Information
            "status": ["stats", "condition", "health"],
            "help": ["?", "commands", "instructions"],
            "quests": ["missions", "tasks", "objectives"],
            # Party commands
            "recruit": ["hire", "enlist", "invite", "add to party"],
            "dismiss": ["fire", "remove from party", "send away"],
            "party": ["companions", "group", "team", "followers"],
            "order": ["tell", "command", "instruct", "direct"],
            "gather": ["collect party", "reunite", "regroup"],
        }

        # Direction words
        self.directions = {
            "north": ["n", "northward", "northwards"],
            "south": ["s", "southward", "southwards"],
            "east": ["e", "eastward", "eastwards"],
            "west": ["w", "westward", "westwards"],
            "up": ["u", "upward", "upwards", "upstairs"],
            "down": ["d", "downward", "downwards", "downstairs"],
            "northeast": ["ne", "north-east"],
            "northwest": ["nw", "north-west"],
            "southeast": ["se", "south-east"],
            "southwest": ["sw", "south-west"],
        }

        # Articles and prepositions to ignore
        self.ignore_words = {
            "the",
            "a",
            "an",
            "at",
            "to",
            "in",
            "on",
            "from",
            "with",
            "of",
            "into",
            "onto",
            "my",
            "some",
        }

        # Question patterns
        self.question_patterns = [
            (r"^(what|where|who|why|how|when) ", "question"),
            (r"^can i ", "ability_check"),
            (r"^is there ", "existence_check"),
        ]

    def normalize_verb(self, verb: str) -> str:
        """Convert synonym to base verb"""
        verb = verb.lower().strip()

        # Check if already a base verb
        if verb in self.verb_map:
            return verb

        # Look for synonym
        for base_verb, synonyms in self.verb_map.items():
            if verb in synonyms:
                return base_verb

        return verb

    def normalize_direction(self, direction: str) -> Optional[str]:
        """Convert direction synonym to base direction"""
        direction = direction.lower().strip()

        # Check if already a base direction
        if direction in self.directions:
            return direction

        # Look for synonym
        for base_dir, synonyms in self.directions.items():
            if direction in synonyms:
                return base_dir

        return None

    def extract_objects(self, text: str) -> List[str]:
        """Extract object names from text, removing articles"""
        words = text.lower().split()
        filtered = [w for w in words if w not in self.ignore_words]
        return [" ".join(filtered)] if filtered else []

    def parse_sentence(self, sentence: str) -> Dict[str, Any]:
        """Parse a natural language sentence into command components"""
        sentence = sentence.strip()

        if not sentence:
            return {"action": None}

        # Special case: "what am i carrying" -> inventory
        if re.match(r"^what (am i|do i) (carrying|have|hold)", sentence.lower()):
            return {"action": "inventory"}

        # Check for questions
        for pattern, q_type in self.question_patterns:
            if re.match(pattern, sentence.lower()):
                return {"action": "question", "question_type": q_type, "text": sentence}

        # Split into words
        words = sentence.lower().split()

        # Try to identify verb (first significant word)
        verb = None
        verb_index = 0

        # Check for multi-word verbs first
        for i in range(len(words)):
            # Try 2-word combinations
            if i < len(words) - 1:
                two_word = f"{words[i]} {words[i+1]}"
                normalized = self.normalize_verb(two_word)
                if normalized in self.verb_map:
                    verb = normalized
                    verb_index = i + 2
                    break

            # Try single word
            normalized = self.normalize_verb(words[i])
            if normalized in self.verb_map:
                verb = normalized
                verb_index = i + 1
                break

        if not verb:
            # Before treating as examine, check if it's a direction
            direction = self.normalize_direction(" ".join(words))
            if direction:
                return {"action": "move", "direction": direction}

            # Check if first word looks like it might be an action verb
            # even if not recognized (e.g., "poke", "touch", "smell")
            # Default these to examine
            if len(words) > 1:
                # Multiple words with unknown verb -> examine the target
                return {"action": "look", "target": " ".join(words[1:])}
            else:
                # Single unknown word -> examine it
                return {"action": "look", "target": " ".join(words)}

        # Extract rest of sentence after verb
        rest = " ".join(words[verb_index:])

        # Special handling for "go in" / "go out" -> movement
        if verb == "go":
            if rest in ["in", "inside"]:
                return {"action": "move", "direction": "in"}
            elif rest in ["out", "outside"]:
                return {"action": "move", "direction": "out"}

        # Check for direction (movement commands)
        direction = self.normalize_direction(rest)
        if direction:
            return {"action": "move", "direction": direction}

        # Check if verb itself is a direction
        direction = self.normalize_direction(verb)
        if direction:
            return {"action": "move", "direction": direction}

        # Special handling for "tell/order X to Y" pattern (party commands)
        # This must come before other verb handling to catch party orders
        if verb in ["order", "tell", "command", "instruct"]:
            if " to " in rest:
                parts = rest.split(" to ", 1)
                return {
                    "action": "party_order",
                    "companion": parts[0].strip() if parts else "",
                    "order": parts[1].strip() if len(parts) > 1 else "",
                }
            # If no "to" pattern, and it's "tell", treat as talk
            elif verb == "tell":
                return {"action": "talk", "target": rest.strip()}

        # Special handling for enter/exit with targets -> movement
        if verb == "enter" and rest:
            # "enter cave" could mean go into cave
            return {"action": "move", "target": rest.strip()}
        if verb == "exit" and rest:
            # "exit building" could mean leave
            return {"action": "move", "target": rest.strip()}

        # Special handling for "leave" - context dependent
        if verb == "drop":
            # "leave the armor" = drop (has object)
            return {"action": "drop", "target": rest.strip()}

        # Special case: bare "leave" with no object = exit
        if verb == "exit" and not rest.strip():
            return {"action": "move", "direction": "out"}

        # Parse prepositions for complex commands
        # "put sword in backpack" -> object: sword, container: backpack
        if " in " in rest or " into " in rest:
            parts = re.split(r" in | into ", rest, 1)
            return {
                "action": verb,
                "object": parts[0].strip() if parts else "",
                "container": parts[1].strip() if len(parts) > 1 else None,
            }

        if " on " in rest or " onto " in rest:
            parts = re.split(r" on | onto ", rest, 1)
            return {
                "action": verb,
                "object": parts[0].strip() if parts else "",
                "target": parts[1].strip() if len(parts) > 1 else None,
            }

        if " to " in rest:
            parts = rest.split(" to ", 1)
            return {
                "action": verb,
                "object": parts[0].strip() if parts else "",
                "target": parts[1].strip() if len(parts) > 1 else None,
            }

        if " about " in rest:
            parts = rest.split(" about ", 1)
            return {
                "action": verb,
                "target": parts[0].strip() if parts else "",
                "topic": parts[1].strip() if len(parts) > 1 else None,
            }

        if " with " in rest:
            parts = rest.split(" with ", 1)
            return {
                "action": verb,
                "object": parts[0].strip() if parts else "",
                "instrument": parts[1].strip() if len(parts) > 1 else None,
            }

        # Simple action + object
        objects = self.extract_objects(rest)
        return {"action": verb, "target": objects[0] if objects else rest.strip()}

    def parse_command(self, command: str) -> Dict[str, Any]:
        """Main entry point for parsing commands"""
        # Handle special commands
        command = command.strip()

        if command.lower() in ["quit", "exit", "q"]:
            return {"action": "quit"}

        if command.lower() in ["help", "?"]:
            return {"action": "help"}

        # Parse as natural language
        return self.parse_sentence(command)

    def get_help_text(self) -> str:
        """Generate comprehensive help text"""
        return """
ADVENTURE CONSTRUCTION SET - COMMANDS

You can type natural language! Examples:
  "go north" or "walk to the north" or just "north"
  "pick up the sword" or "get sword" or "take the rusty blade"
  "talk to the wizard" or "speak with wizard" or "chat to wizard"
  "look at the painting" or "examine painting" or "inspect the art"

MOVEMENT:
  north, south, east, west, up, down (or n, s, e, w, u, d)
  go [direction], walk [direction], move [direction]

LOOKING AROUND:
  look - Look at current location
  look at [object] - Examine something
  examine [object], inspect [object], check [object]
  search - Search the area for hidden items

INVENTORY:
  inventory (or i) - See what you're carrying
  get [item], take [item], pick up [item]
  drop [item], put down [item]
  put [item] in [container] - Store items

EQUIPMENT:
  equip [item], wear [item], wield [item]
  unequip [item], remove [item], take off [item]

COMBAT:
  attack [enemy], fight [enemy], kill [enemy]
  flee, run away, escape, retreat

INTERACTION:
  talk to [npc], speak with [npc], chat to [npc]
  ask [npc] about [topic]
  give [item] to [npc]
  trade with [npc], buy, sell

USING ITEMS:
  use [item] - Use an item
  read [item] - Read books, scrolls, signs
  drink [potion], eat [food]
  open [door/chest], close [door/chest]

PARTY (Companions):
  party - View your companions
  recruit [npc], invite [npc] to join
  dismiss [companion], send [companion] away
  order [companion] to [action]

QUESTS:
  quests - View active quests
  quest [number] - View quest details

INFORMATION:
  status - View your character stats
  help - This help text
  save - Save your game
  load - Load a saved game

You can be creative! The parser understands many ways to say things.
Try natural sentences like "Can I open the door?" or "What's in the chest?"
"""


# Companion/Party member class
class CompanionStance(Enum):
    """Combat/behavior stances for companions"""

    AGGRESSIVE = "aggressive"  # Focus on damage
    DEFENSIVE = "defensive"  # Protect party
    SUPPORT = "support"  # Heal/buff others
    PASSIVE = "passive"  # Avoid combat
    FOLLOW = "follow"  # Follow player commands only


class Companion:
    """Represents an NPC companion in the party"""

    def __init__(self, npc_id: int, name: str, role: str = "fighter"):
        self.npc_id = npc_id
        self.name = name
        self.role = role  # fighter, mage, healer, rogue, etc.
        self.loyalty = 50  # 0-100, affects whether they stay
        self.current_health = 20
        self.max_health = 20
        self.level = 1
        self.experience = 0

        # AI and behavior
        self.stance = CompanionStance.AGGRESSIVE
        self.is_waiting = False  # If told to wait somewhere
        self.wait_location = None  # Room ID where waiting
        self.auto_loot = True  # Automatically pick up items
        self.auto_heal_threshold = 30  # % health to auto-heal at

        # Combat stats based on role
        if role == "fighter":
            self.hardiness = 15
            self.agility = 10
            self.attack_bonus = 3
            self.default_stance = CompanionStance.AGGRESSIVE
        elif role == "mage":
            self.hardiness = 8
            self.agility = 12
            self.attack_bonus = 1
            self.can_cast_spells = True
            self.default_stance = CompanionStance.SUPPORT
        elif role == "healer":
            self.hardiness = 10
            self.agility = 10
            self.attack_bonus = 1
            self.can_heal = True
            self.default_stance = CompanionStance.SUPPORT
        elif role == "rogue":
            self.hardiness = 10
            self.agility = 16
            self.attack_bonus = 2
            self.can_pick_locks = True
            self.default_stance = CompanionStance.AGGRESSIVE
        else:
            self.hardiness = 12
            self.agility = 12
            self.attack_bonus = 2
            self.default_stance = CompanionStance.AGGRESSIVE

        self.stance = self.default_stance

        self.inventory = []
        self.equipped_weapon = None

    def take_damage(self, amount: int):
        """Companion takes damage"""
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

    def heal(self, amount: int):
        """Heal the companion"""
        self.current_health = min(self.current_health + amount, self.max_health)

    def is_alive(self) -> bool:
        """Check if companion is still alive"""
        return self.current_health > 0

    def get_attack_damage(self) -> int:
        """Calculate attack damage"""
        import random

        base_damage = random.randint(1, 6) + self.attack_bonus
        return base_damage

    def improve_loyalty(self, amount: int = 5):
        """Increase loyalty"""
        self.loyalty = min(100, self.loyalty + amount)

    def decrease_loyalty(self, amount: int = 5):
        """Decrease loyalty"""
        self.loyalty = max(0, self.loyalty - amount)

    def will_stay(self) -> bool:
        """Check if companion will remain in party"""
        return self.loyalty >= 30

    def set_stance(self, stance: CompanionStance):
        """Change companion's combat stance"""
        self.stance = stance

    def tell_to_wait(self, room_id: int):
        """Tell companion to wait at location"""
        self.is_waiting = True
        self.wait_location = room_id

    def tell_to_follow(self):
        """Tell companion to resume following"""
        self.is_waiting = False
        self.wait_location = None

    def should_act_in_combat(self) -> bool:
        """Check if companion should act based on stance"""
        if self.stance == CompanionStance.PASSIVE:
            return False
        if self.stance == CompanionStance.FOLLOW:
            return False  # Waits for explicit orders
        return True

    def get_health_percent(self) -> int:
        """Get current health as percentage"""
        if self.max_health == 0:
            return 0
        return int((self.current_health / self.max_health) * 100)

    def should_auto_heal(self) -> bool:
        """Check if companion should heal themselves"""
        if not hasattr(self, "can_heal"):
            return False
        if self.stance == CompanionStance.PASSIVE:
            return False
        return self.get_health_percent() < self.auto_heal_threshold

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "role": self.role,
            "loyalty": self.loyalty,
            "current_health": self.current_health,
            "max_health": self.max_health,
            "level": self.level,
            "hardiness": self.hardiness,
            "agility": self.agility,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "stance": self.stance.value,
            "is_waiting": self.is_waiting,
            "wait_location": self.wait_location,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Companion":
        """Deserialize from dictionary"""
        companion = cls(data["npc_id"], data["name"], data.get("role", "fighter"))
        companion.loyalty = data.get("loyalty", 50)
        companion.current_health = data.get("current_health", 20)
        companion.max_health = data.get("max_health", 20)
        companion.level = data.get("level", 1)
        companion.inventory = data.get("inventory", [])
        companion.equipped_weapon = data.get("equipped_weapon")
        companion.stance = CompanionStance(data.get("stance", "aggressive"))
        companion.is_waiting = data.get("is_waiting", False)
        companion.wait_location = data.get("wait_location")
        return companion
