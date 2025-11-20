#!/usr/bin/env python3
"""
Adventure Construction Set - Modding & Scripting Support
Allow adventure creators to extend functionality with Python scripts
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import sys
from io import StringIO


class EventType(Enum):
    """Types of events that can trigger scripts"""

    ON_ENTER_ROOM = "on_enter_room"
    ON_EXIT_ROOM = "on_exit_room"
    ON_TAKE_ITEM = "on_take_item"
    ON_DROP_ITEM = "on_drop_item"
    ON_ATTACK = "on_attack"
    ON_KILL = "on_kill"
    ON_DEATH = "on_death"
    ON_TALK = "on_talk"
    ON_USE_ITEM = "on_use_item"
    ON_EXAMINE = "on_examine"
    ON_COMMAND = "on_command"  # Before any command
    ON_UNKNOWN_COMMAND = "on_unknown_command"
    ON_SAVE = "on_save"
    ON_LOAD = "on_load"


@dataclass
class ScriptHook:
    """A script that runs in response to an event"""

    event: EventType
    script_code: str
    priority: int = 0  # Higher priority runs first
    enabled: bool = True
    filter_params: Dict[str, Any] = field(default_factory=dict)

    def matches_filter(self, event_data: Dict[str, Any]) -> bool:
        """Check if event matches filter parameters"""
        if not self.filter_params:
            return True

        for key, value in self.filter_params.items():
            if key not in event_data:
                return False
            if isinstance(value, list):
                if event_data[key] not in value:
                    return False
            elif event_data[key] != value:
                return False
        return True


@dataclass
class CustomCommand:
    """A custom command added by a mod"""

    verb: str
    aliases: List[str]
    handler_code: str
    help_text: str = ""
    hidden: bool = False


class ScriptContext:
    """Safe execution context for mod scripts"""

    def __init__(self, engine=None):
        self.engine = engine
        self.output_buffer = []
        self._allowed_modules = {
            "math",
            "random",
            "re",
            "json",
            "datetime",
            "collections",
        }

    def print(self, *args, **kwargs):
        """Capture print output"""
        msg = " ".join(str(arg) for arg in args)
        self.output_buffer.append(msg)

    def echo(self, message: str):
        """Echo message to player"""
        self.output_buffer.append(message)

    def get_player(self):
        """Get player object"""
        if self.engine:
            return self.engine.player
        return None

    def get_room(self, room_id: Optional[int] = None):
        """Get room object"""
        if not self.engine:
            return None
        if room_id is None:
            return self.engine.current_room
        return self.engine.rooms.get(room_id)

    def get_npc(self, name: str):
        """Get NPC by name"""
        if not self.engine:
            return None
        for npc in self.engine.current_room.npcs:
            if npc.name.lower() == name.lower():
                return npc
        return None

    def get_item(self, name: str):
        """Get item by name from room or inventory"""
        if not self.engine:
            return None

        # Check player inventory
        for item in self.engine.player.inventory:
            if item.name.lower() == name.lower():
                return item

        # Check room
        for item in self.engine.current_room.items:
            if item.name.lower() == name.lower():
                return item
        return None

    def spawn_item(self, item_name: str, room_id: Optional[int] = None):
        """Spawn a new item"""
        if not self.engine:
            return None
        # Would need to create item from template
        # Placeholder for now
        self.echo(f"[Spawned {item_name}]")

    def spawn_npc(self, npc_name: str, room_id: Optional[int] = None):
        """Spawn a new NPC"""
        if not self.engine:
            return None
        # Placeholder
        self.echo(f"[Spawned NPC: {npc_name}]")

    def set_flag(self, flag_name: str, value: Any = True):
        """Set a global flag"""
        if self.engine:
            if not hasattr(self.engine, "script_flags"):
                self.engine.script_flags = {}
            self.engine.script_flags[flag_name] = value

    def get_flag(self, flag_name: str, default: Any = None):
        """Get a global flag"""
        if self.engine and hasattr(self.engine, "script_flags"):
            return self.engine.script_flags.get(flag_name, default)
        return default

    def has_flag(self, flag_name: str) -> bool:
        """Check if flag exists and is truthy"""
        return bool(self.get_flag(flag_name))


class ModdingSystem:
    """System for loading and executing mod scripts"""

    def __init__(self, engine=None):
        self.engine = engine
        self.hooks: Dict[EventType, List[ScriptHook]] = {
            event: [] for event in EventType
        }
        self.custom_commands: Dict[str, CustomCommand] = {}
        self.script_context = ScriptContext(engine)

    def register_hook(self, hook: ScriptHook):
        """Register an event hook"""
        if hook.event not in self.hooks:
            self.hooks[hook.event] = []
        self.hooks[hook.event].append(hook)
        # Sort by priority (highest first)
        self.hooks[hook.event].sort(key=lambda h: h.priority, reverse=True)

    def register_command(self, command: CustomCommand):
        """Register a custom command"""
        self.custom_commands[command.verb] = command
        for alias in command.aliases:
            self.custom_commands[alias] = command

    def trigger_event(self, event: EventType, event_data: Dict[str, Any]) -> List[str]:
        """Trigger an event and run associated hooks"""
        output = []

        if event not in self.hooks:
            return output

        for hook in self.hooks[event]:
            if not hook.enabled:
                continue
            if not hook.matches_filter(event_data):
                continue

            try:
                result = self._execute_script(hook.script_code, event_data)
                if result:
                    output.extend(result)
            except Exception as e:
                output.append(f"[Script Error: {e}]")

        return output

    def execute_custom_command(self, verb: str, args: str) -> Optional[List[str]]:
        """Execute a custom command if registered"""
        if verb not in self.custom_commands:
            return None

        command = self.custom_commands[verb]
        event_data = {"verb": verb, "args": args, "command": f"{verb} {args}"}

        try:
            return self._execute_script(command.handler_code, event_data)
        except Exception as e:
            return [f"[Command Error: {e}]"]

    def _execute_script(self, code: str, event_data: Dict[str, Any]) -> List[str]:
        """Execute script code in safe context"""
        # Reset output buffer
        self.script_context.output_buffer = []

        # Create execution namespace
        namespace = {
            "ctx": self.script_context,
            "data": event_data,
            "print": self.script_context.print,
            "echo": self.script_context.echo,
            "player": self.script_context.get_player(),
            "room": self.script_context.get_room(),
            # Utility functions
            "get_npc": self.script_context.get_npc,
            "get_item": self.script_context.get_item,
            "spawn_item": self.script_context.spawn_item,
            "spawn_npc": self.script_context.spawn_npc,
            "set_flag": self.script_context.set_flag,
            "get_flag": self.script_context.get_flag,
            "has_flag": self.script_context.has_flag,
        }

        # Import allowed modules
        for module in self.script_context._allowed_modules:
            try:
                namespace[module] = __import__(module)
            except ImportError:
                pass

        # Execute code
        try:
            exec(code, namespace)
        except Exception as e:
            return [f"[Script Error: {e}]"]

        return self.script_context.output_buffer

    def load_mod_file(self, filepath: str) -> bool:
        """Load a mod from a Python file"""
        try:
            with open(filepath, "r") as f:
                code = f.read()

            # Execute mod file to register hooks/commands
            namespace = {
                "register_hook": self.register_hook,
                "register_command": self.register_command,
                "ScriptHook": ScriptHook,
                "CustomCommand": CustomCommand,
                "EventType": EventType,
            }

            exec(code, namespace)
            return True
        except Exception as e:
            print(f"Error loading mod {filepath}: {e}")
            return False

    def get_custom_command_help(self) -> List[str]:
        """Get help text for custom commands"""
        help_lines = []

        seen = set()
        for verb, command in self.custom_commands.items():
            if command.verb in seen or command.hidden:
                continue
            seen.add(command.verb)

            aliases = ", ".join(command.aliases) if command.aliases else ""
            help_text = command.help_text or "Custom command"

            if aliases:
                help_lines.append(f"  {command.verb} ({aliases}) - {help_text}")
            else:
                help_lines.append(f"  {command.verb} - {help_text}")

        return help_lines

    def to_dict(self) -> Dict:
        """Serialize mod state"""
        return {
            "script_flags": getattr(self.engine, "script_flags", {}),
            "enabled_hooks": [
                {"event": hook.event.value, "enabled": hook.enabled}
                for hooks in self.hooks.values()
                for hook in hooks
            ],
        }

    def from_dict(self, data: Dict):
        """Restore mod state"""
        if "script_flags" in data and self.engine:
            self.engine.script_flags = data["script_flags"]

        if "enabled_hooks" in data:
            for hook_data in data["enabled_hooks"]:
                event = EventType(hook_data["event"])
                # Find matching hook and set enabled state
                for hook in self.hooks[event]:
                    # Would need better hook identification
                    hook.enabled = hook_data["enabled"]


# Example mod file format:
"""
# example_mod.py - Example mod for ACS

# Register a hook that runs when entering a room
hook = ScriptHook(
    event=EventType.ON_ENTER_ROOM,
    script_code='''
if room.id == 5:
    echo("You feel a strange presence in this room...")
    set_flag("visited_haunted_room", True)
''',
    filter_params={'room_id': 5}
)
register_hook(hook)

# Register a custom command
command = CustomCommand(
    verb="dance",
    aliases=["boogie"],
    help_text="Dance around like nobody's watching",
    handler_code='''
echo("You dance awkwardly. Everyone stares.")
if has_flag("dance_master"):
    echo("Actually, you're quite good at this!")
else:
    echo("Maybe practice more...")
'''
)
register_command(command)
"""
