#!/usr/bin/env python3
"""
Adventure Construction Set - Environmental Storytelling System
Adds dynamic room states, inspectable objects, time/weather effects
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random


class TimeOfDay(Enum):
    """Time periods that affect descriptions"""

    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class Weather(Enum):
    """Weather conditions"""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINING = "raining"
    STORMING = "storming"
    SNOWING = "snowing"
    FOGGY = "foggy"
    WINDY = "windy"


@dataclass
class InspectableObject:
    """An object in a room that can be examined for details"""

    id: str
    name: str
    short_desc: str  # What you see from room description
    long_desc: str  # What you see when examining
    keywords: List[str] = field(default_factory=list)
    hidden: bool = False  # Requires search to find
    revealed_on_search: bool = False
    contains_item_id: Optional[int] = None  # Item revealed on examination
    triggers_event: Optional[str] = None  # Event ID to trigger

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "short_desc": self.short_desc,
            "long_desc": self.long_desc,
            "keywords": self.keywords,
            "hidden": self.hidden,
            "revealed_on_search": self.revealed_on_search,
            "contains_item_id": self.contains_item_id,
            "triggers_event": self.triggers_event,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InspectableObject":
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            short_desc=data["short_desc"],
            long_desc=data["long_desc"],
            keywords=data.get("keywords", []),
            hidden=data.get("hidden", False),
            revealed_on_search=data.get("revealed_on_search", False),
            contains_item_id=data.get("contains_item_id"),
            triggers_event=data.get("triggers_event"),
        )


@dataclass
class RoomState:
    """Tracks the state of a room that can change over time"""

    room_id: int
    state_name: str = "default"  # current state
    visited_count: int = 0
    last_visit_time: Optional[datetime] = None
    objects_revealed: List[str] = field(default_factory=list)
    custom_flags: Dict[str, bool] = field(default_factory=dict)

    # Time-based states
    description_variants: Dict[str, str] = field(default_factory=dict)

    def increment_visit(self):
        """Record a visit to this room"""
        self.visited_count += 1
        self.last_visit_time = datetime.now()

    def set_state(self, state_name: str):
        """Change room state"""
        self.state_name = state_name

    def reveal_object(self, object_id: str):
        """Mark object as revealed"""
        if object_id not in self.objects_revealed:
            self.objects_revealed.append(object_id)

    def is_object_revealed(self, object_id: str) -> bool:
        """Check if object has been revealed"""
        return object_id in self.objects_revealed

    def get_description(
        self, base_desc: str, time_of_day: TimeOfDay, weather: Weather
    ) -> str:
        """Get room description modified by state, time, and weather"""
        desc = base_desc

        # Apply state variant if exists
        state_key = f"state_{self.state_name}"
        if state_key in self.description_variants:
            desc = self.description_variants[state_key]

        # Apply time variant if exists
        time_key = f"time_{time_of_day.value}"
        if time_key in self.description_variants:
            desc += f"\n{self.description_variants[time_key]}"

        # Apply weather variant if exists
        weather_key = f"weather_{weather.value}"
        if weather_key in self.description_variants:
            desc += f"\n{self.description_variants[weather_key]}"

        return desc


class EnvironmentalSystem:
    """Manages environmental effects and dynamic world state"""

    def __init__(self):
        self.current_time = TimeOfDay.MORNING
        self.current_weather = Weather.CLEAR
        self.turn_count = 0
        self.room_states: Dict[int, RoomState] = {}
        self.room_objects: Dict[int, List[InspectableObject]] = {}
        self.ambient_messages: Dict[int, List[str]] = {}

        # Time progression settings
        self.turns_per_hour = 20
        self.weather_change_chance = 0.05

    def advance_time(self):
        """Progress time based on turns"""
        self.turn_count += 1

        if self.turn_count % self.turns_per_hour == 0:
            self._progress_time_of_day()

        if random.random() < self.weather_change_chance:
            self._change_weather()

    def _progress_time_of_day(self):
        """Move to next time period"""
        times = list(TimeOfDay)
        current_idx = times.index(self.current_time)
        next_idx = (current_idx + 1) % len(times)
        self.current_time = times[next_idx]

    def _change_weather(self):
        """Randomly change weather"""
        weathers = list(Weather)
        # Favor transitions between similar conditions
        current_idx = weathers.index(self.current_weather)

        # Adjacent weather is more likely
        options = [current_idx]
        if current_idx > 0:
            options.append(current_idx - 1)
        if current_idx < len(weathers) - 1:
            options.append(current_idx + 1)

        new_idx = random.choice(options)
        self.current_weather = weathers[new_idx]

    def get_time_description(self) -> str:
        """Get description of current time"""
        descriptions = {
            TimeOfDay.DAWN: "The sun is just beginning to rise.",
            TimeOfDay.MORNING: "It's a fresh morning.",
            TimeOfDay.NOON: "The sun is high overhead.",
            TimeOfDay.AFTERNOON: "The afternoon sun warms the air.",
            TimeOfDay.DUSK: "The sun is setting on the horizon.",
            TimeOfDay.EVENING: "Evening approaches.",
            TimeOfDay.NIGHT: "Night has fallen.",
            TimeOfDay.MIDNIGHT: "It's the dead of night.",
        }
        return descriptions.get(self.current_time, "")

    def get_weather_description(self) -> str:
        """Get description of current weather"""
        descriptions = {
            Weather.CLEAR: "The sky is clear.",
            Weather.CLOUDY: "Clouds cover the sky.",
            Weather.RAINING: "Rain falls steadily.",
            Weather.STORMING: "A fierce storm rages!",
            Weather.SNOWING: "Snow drifts down gently.",
            Weather.FOGGY: "Thick fog obscures your vision.",
            Weather.WINDY: "Strong winds blow.",
        }
        return descriptions.get(self.current_weather, "")

    def get_or_create_room_state(self, room_id: int) -> RoomState:
        """Get or create room state"""
        if room_id not in self.room_states:
            self.room_states[room_id] = RoomState(room_id=room_id)
        return self.room_states[room_id]

    def add_room_object(self, room_id: int, obj: InspectableObject):
        """Add inspectable object to room"""
        if room_id not in self.room_objects:
            self.room_objects[room_id] = []
        self.room_objects[room_id].append(obj)

    def get_room_objects(
        self, room_id: int, include_hidden: bool = False
    ) -> List[InspectableObject]:
        """Get inspectable objects in room"""
        objects = self.room_objects.get(room_id, [])

        if include_hidden:
            return objects

        # Only return revealed objects
        room_state = self.get_or_create_room_state(room_id)
        return [
            obj
            for obj in objects
            if not obj.hidden or room_state.is_object_revealed(obj.id)
        ]

    def search_room(self, room_id: int) -> List[InspectableObject]:
        """Search room for hidden objects"""
        room_state = self.get_or_create_room_state(room_id)
        found = []

        for obj in self.room_objects.get(room_id, []):
            if obj.hidden and obj.revealed_on_search:
                if not room_state.is_object_revealed(obj.id):
                    room_state.reveal_object(obj.id)
                    found.append(obj)

        return found

    def find_object_by_keyword(
        self, room_id: int, keyword: str
    ) -> Optional[InspectableObject]:
        """Find object in room by keyword"""
        keyword = keyword.lower()
        objects = self.get_room_objects(room_id, include_hidden=False)

        for obj in objects:
            if keyword in obj.name.lower():
                return obj
            if any(keyword in kw.lower() for kw in obj.keywords):
                return obj

        return None

    def get_ambient_message(self, room_id: int) -> Optional[str]:
        """Get random ambient message for room"""
        messages = self.ambient_messages.get(room_id, [])
        if messages and random.random() < 0.3:  # 30% chance
            return random.choice(messages)
        return None

    def add_ambient_message(self, room_id: int, message: str):
        """Add ambient message to room"""
        if room_id not in self.ambient_messages:
            self.ambient_messages[room_id] = []
        self.ambient_messages[room_id].append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize environmental system"""
        return {
            "current_time": self.current_time.value,
            "current_weather": self.current_weather.value,
            "turn_count": self.turn_count,
            "room_states": {
                str(room_id): {
                    "state_name": state.state_name,
                    "visited_count": state.visited_count,
                    "objects_revealed": state.objects_revealed,
                    "custom_flags": state.custom_flags,
                }
                for room_id, state in self.room_states.items()
            },
            "room_objects": {
                str(room_id): [obj.to_dict() for obj in objects]
                for room_id, objects in self.room_objects.items()
            },
            "ambient_messages": {str(k): v for k, v in self.ambient_messages.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentalSystem":
        """Deserialize environmental system"""
        system = cls()
        system.current_time = TimeOfDay(data.get("current_time", "morning"))
        system.current_weather = Weather(data.get("current_weather", "clear"))
        system.turn_count = data.get("turn_count", 0)

        # Restore room states
        for room_id_str, state_data in data.get("room_states", {}).items():
            room_id = int(room_id_str)
            state = RoomState(room_id=room_id)
            state.state_name = state_data.get("state_name", "default")
            state.visited_count = state_data.get("visited_count", 0)
            state.objects_revealed = state_data.get("objects_revealed", [])
            state.custom_flags = state_data.get("custom_flags", {})
            system.room_states[room_id] = state

        # Restore room objects
        for room_id_str, objects_data in data.get("room_objects", {}).items():
            room_id = int(room_id_str)
            system.room_objects[room_id] = [
                InspectableObject.from_dict(obj_data) for obj_data in objects_data
            ]

        # Restore ambient messages
        for room_id_str, messages in data.get("ambient_messages", {}).items():
            system.ambient_messages[int(room_id_str)] = messages

        return system
