"""
Data service for managing game entities (rooms, items, monsters)
"""

from typing import Dict, Any, Optional, List
from dataclasses import asdict
import logging

from core.services import Service


class DataService(Service):
    """
    Manages game data entities

    Provides CRUD operations and queries for:
    - Rooms
    - Items
    - Monsters/NPCs
    - Custom entities
    """

    def __init__(self):
        self.logger = logging.getLogger("DataService")
        self._data_store: Dict[str, Dict[int, Any]] = {
            "rooms": {},
            "items": {},
            "monsters": {},
        }

    def initialize(self, config: Dict[str, Any]):
        """Initialize the data service"""
        self.logger.info("Data service initialized")

    def shutdown(self):
        """Cleanup"""
        self._data_store.clear()

    # Room operations
    def add_room(self, room_id: int, room_data: Any):
        """Add a room to the data store"""
        self._data_store["rooms"][room_id] = room_data

    def get_room(self, room_id: int) -> Optional[Any]:
        """Get a room by ID"""
        return self._data_store["rooms"].get(room_id)

    def get_all_rooms(self) -> Dict[int, Any]:
        """Get all rooms"""
        return self._data_store["rooms"].copy()

    def remove_room(self, room_id: int):
        """Remove a room"""
        if room_id in self._data_store["rooms"]:
            del self._data_store["rooms"][room_id]

    # Item operations
    def add_item(self, item_id: int, item_data: Any):
        """Add an item to the data store"""
        self._data_store["items"][item_id] = item_data

    def get_item(self, item_id: int) -> Optional[Any]:
        """Get an item by ID"""
        return self._data_store["items"].get(item_id)

    def get_all_items(self) -> Dict[int, Any]:
        """Get all items"""
        return self._data_store["items"].copy()

    def find_items_by_location(self, location: int) -> List[Any]:
        """Find items at a location"""
        return [
            item
            for item in self._data_store["items"].values()
            if hasattr(item, "location") and item.location == location
        ]

    def remove_item(self, item_id: int):
        """Remove an item"""
        if item_id in self._data_store["items"]:
            del self._data_store["items"][item_id]

    # Monster operations
    def add_monster(self, monster_id: int, monster_data: Any):
        """Add a monster to the data store"""
        self._data_store["monsters"][monster_id] = monster_data

    def get_monster(self, monster_id: int) -> Optional[Any]:
        """Get a monster by ID"""
        return self._data_store["monsters"].get(monster_id)

    def get_all_monsters(self) -> Dict[int, Any]:
        """Get all monsters"""
        return self._data_store["monsters"].copy()

    def find_monsters_by_room(self, room_id: int) -> List[Any]:
        """Find monsters in a room"""
        return [
            monster
            for monster in self._data_store["monsters"].values()
            if hasattr(monster, "room_id") and monster.room_id == room_id
        ]

    def remove_monster(self, monster_id: int):
        """Remove a monster"""
        if monster_id in self._data_store["monsters"]:
            del self._data_store["monsters"][monster_id]

    # Generic operations
    def add_entity(self, entity_type: str, entity_id: int, entity_data: Any):
        """Add a generic entity"""
        if entity_type not in self._data_store:
            self._data_store[entity_type] = {}
        self._data_store[entity_type][entity_id] = entity_data

    def get_entity(self, entity_type: str, entity_id: int) -> Optional[Any]:
        """Get a generic entity"""
        if entity_type in self._data_store:
            return self._data_store[entity_type].get(entity_id)
        return None

    def clear_all(self):
        """Clear all data"""
        for store in self._data_store.values():
            store.clear()

    def import_data(self, data: Dict[str, Any]):
        """
        Import data from adventure file

        Args:
            data: Dictionary with 'rooms', 'items', 'monsters' keys
        """
        if "rooms" in data:
            self._data_store["rooms"] = data["rooms"]
        if "items" in data:
            self._data_store["items"] = data["items"]
        if "monsters" in data:
            self._data_store["monsters"] = data["monsters"]

    def export_data(self) -> Dict[str, Any]:
        """Export all data for saving"""
        return {
            "rooms": self._data_store["rooms"],
            "items": self._data_store["items"],
            "monsters": self._data_store["monsters"],
        }
