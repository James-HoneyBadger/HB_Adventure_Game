#!/usr/bin/env python3
"""
Adventure Construction Set - Journal & Note-Taking System
Automatic event logging, manual notes, quest tracking, and map annotations
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class JournalEntryType(Enum):
    """Types of journal entries"""

    AUTO_EVENT = "auto_event"
    MANUAL_NOTE = "manual_note"
    QUEST_UPDATE = "quest_update"
    NPC_CONVERSATION = "npc_conversation"
    DISCOVERY = "discovery"
    COMBAT = "combat"
    MAP_ANNOTATION = "map_annotation"


class EntryImportance(Enum):
    """Importance levels for filtering"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class JournalEntry:
    """A single journal entry"""

    id: int
    timestamp: datetime
    entry_type: JournalEntryType
    importance: EntryImportance
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    related_npc: Optional[str] = None
    related_quest: Optional[str] = None
    room_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entry"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "entry_type": self.entry_type.value,
            "importance": self.importance.value,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "related_npc": self.related_npc,
            "related_quest": self.related_quest,
            "room_id": self.room_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JournalEntry":
        """Deserialize entry"""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            entry_type=JournalEntryType(data["entry_type"]),
            importance=EntryImportance(data["importance"]),
            title=data["title"],
            content=data["content"],
            tags=data.get("tags", []),
            related_npc=data.get("related_npc"),
            related_quest=data.get("related_quest"),
            room_id=data.get("room_id"),
        )


@dataclass
class MapAnnotation:
    """Annotation for a specific room"""

    room_id: int
    annotation: str
    icon: str = "📍"  # Emoji or symbol
    color: str = "yellow"
    created: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize annotation"""
        return {
            "room_id": self.room_id,
            "annotation": self.annotation,
            "icon": self.icon,
            "color": self.color,
            "created": self.created.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MapAnnotation":
        """Deserialize annotation"""
        return cls(
            room_id=data["room_id"],
            annotation=data["annotation"],
            icon=data.get("icon", "📍"),
            color=data.get("color", "yellow"),
            created=datetime.fromisoformat(data["created"]),
        )


class QuestHint:
    """Contextual hint for quest progression"""

    def __init__(self, quest_id: str, hint_text: str, condition: Optional[str] = None):
        self.quest_id = quest_id
        self.hint_text = hint_text
        self.condition = condition  # Condition when hint should show
        self.shown = False

    def should_show(self, quest_state: Dict[str, Any]) -> bool:
        """Check if hint should be shown"""
        if self.shown:
            return False
        if not self.condition:
            return True
        # Simple condition checking (can be enhanced)
        return quest_state.get(self.condition, False)


class AdventureJournal:
    """Complete journal system for tracking adventure progress"""

    def __init__(self):
        self.entries: List[JournalEntry] = []
        self.next_entry_id = 1
        self.map_annotations: Dict[int, MapAnnotation] = {}
        self.quest_hints: Dict[str, List[QuestHint]] = {}
        self.bookmarks: List[int] = []  # Bookmarked entry IDs

        # Auto-logging settings
        self.auto_log_enabled = True
        self.auto_log_combat = True
        self.auto_log_discoveries = True
        self.auto_log_conversations = True

    def add_entry(
        self,
        entry_type: JournalEntryType,
        title: str,
        content: str,
        importance: EntryImportance = EntryImportance.NORMAL,
        tags: List[str] = None,
        **kwargs,
    ) -> JournalEntry:
        """Add a new journal entry"""
        entry = JournalEntry(
            id=self.next_entry_id,
            timestamp=datetime.now(),
            entry_type=entry_type,
            importance=importance,
            title=title,
            content=content,
            tags=tags or [],
            **kwargs,
        )
        self.entries.append(entry)
        self.next_entry_id += 1
        return entry

    def add_manual_note(self, note: str, tags: List[str] = None) -> JournalEntry:
        """Add a manual note from the player"""
        return self.add_entry(
            JournalEntryType.MANUAL_NOTE, "Personal Note", note, tags=tags or []
        )

    def log_event(
        self,
        title: str,
        content: str,
        importance: EntryImportance = EntryImportance.NORMAL,
        **kwargs,
    ) -> Optional[JournalEntry]:
        """Auto-log an event"""
        if not self.auto_log_enabled:
            return None
        return self.add_entry(
            JournalEntryType.AUTO_EVENT, title, content, importance, **kwargs
        )

    def log_combat(
        self, enemy_name: str, outcome: str, damage_dealt: int, damage_taken: int
    ) -> Optional[JournalEntry]:
        """Auto-log combat encounter"""
        if not self.auto_log_combat:
            return None
        content = (
            f"Battled {enemy_name}. Outcome: {outcome}. "
            f"Dealt {damage_dealt} damage, took {damage_taken} damage."
        )
        return self.add_entry(
            JournalEntryType.COMBAT,
            f"Combat: {enemy_name}",
            content,
            EntryImportance.NORMAL,
            tags=["combat", enemy_name.lower()],
        )

    def log_discovery(
        self, what: str, where: str, room_id: int
    ) -> Optional[JournalEntry]:
        """Auto-log a discovery"""
        if not self.auto_log_discoveries:
            return None
        return self.add_entry(
            JournalEntryType.DISCOVERY,
            f"Discovered: {what}",
            f"Found {what} in {where}",
            EntryImportance.HIGH,
            tags=["discovery"],
            room_id=room_id,
        )

    def log_conversation(
        self, npc_name: str, topic: str, summary: str
    ) -> Optional[JournalEntry]:
        """Auto-log NPC conversation"""
        if not self.auto_log_conversations:
            return None
        return self.add_entry(
            JournalEntryType.NPC_CONVERSATION,
            f"Talked with {npc_name}",
            f"Discussed {topic}. {summary}",
            EntryImportance.NORMAL,
            tags=["conversation", npc_name.lower()],
            related_npc=npc_name,
        )

    def log_quest_update(
        self, quest_id: str, quest_name: str, update: str
    ) -> JournalEntry:
        """Log quest progress"""
        return self.add_entry(
            JournalEntryType.QUEST_UPDATE,
            f"Quest: {quest_name}",
            update,
            EntryImportance.HIGH,
            tags=["quest", quest_id],
            related_quest=quest_id,
        )

    def annotate_room(
        self, room_id: int, annotation: str, icon: str = "📍", color: str = "yellow"
    ):
        """Add map annotation for a room"""
        self.map_annotations[room_id] = MapAnnotation(room_id, annotation, icon, color)

    def get_room_annotation(self, room_id: int) -> Optional[MapAnnotation]:
        """Get annotation for a room"""
        return self.map_annotations.get(room_id)

    def remove_room_annotation(self, room_id: int) -> bool:
        """Remove room annotation"""
        if room_id in self.map_annotations:
            del self.map_annotations[room_id]
            return True
        return False

    def search_entries(self, query: str) -> List[JournalEntry]:
        """Search journal entries by text"""
        query_lower = query.lower()
        results = []
        for entry in self.entries:
            if (
                query_lower in entry.title.lower()
                or query_lower in entry.content.lower()
                or any(query_lower in tag.lower() for tag in entry.tags)
            ):
                results.append(entry)
        return results

    def get_entries_by_tag(self, tag: str) -> List[JournalEntry]:
        """Get entries with specific tag"""
        tag_lower = tag.lower()
        return [e for e in self.entries if any(tag_lower == t.lower() for t in e.tags)]

    def get_entries_by_type(self, entry_type: JournalEntryType) -> List[JournalEntry]:
        """Get entries of specific type"""
        return [e for e in self.entries if e.entry_type == entry_type]

    def get_recent_entries(self, count: int = 10) -> List[JournalEntry]:
        """Get most recent entries"""
        return list(reversed(self.entries[-count:]))

    def get_important_entries(
        self, min_importance: EntryImportance = EntryImportance.HIGH
    ) -> List[JournalEntry]:
        """Get important entries"""
        return [e for e in self.entries if e.importance.value >= min_importance.value]

    def bookmark_entry(self, entry_id: int):
        """Bookmark an entry"""
        if entry_id not in self.bookmarks:
            self.bookmarks.append(entry_id)

    def unbookmark_entry(self, entry_id: int):
        """Remove bookmark"""
        if entry_id in self.bookmarks:
            self.bookmarks.remove(entry_id)

    def get_bookmarked_entries(self) -> List[JournalEntry]:
        """Get bookmarked entries"""
        return [e for e in self.entries if e.id in self.bookmarks]

    def add_quest_hint(self, quest_id: str, hint: QuestHint):
        """Add hint for a quest"""
        if quest_id not in self.quest_hints:
            self.quest_hints[quest_id] = []
        self.quest_hints[quest_id].append(hint)

    def get_quest_hints(
        self, quest_id: str, quest_state: Dict[str, Any] = None
    ) -> List[QuestHint]:
        """Get available hints for quest"""
        hints = self.quest_hints.get(quest_id, [])
        if quest_state is None:
            return [h for h in hints if not h.shown]
        return [h for h in hints if h.should_show(quest_state)]

    def show_hint(self, quest_id: str, hint_index: int):
        """Mark hint as shown"""
        hints = self.quest_hints.get(quest_id, [])
        if 0 <= hint_index < len(hints):
            hints[hint_index].shown = True

    def get_quest_entries(self, quest_id: str) -> List[JournalEntry]:
        """Get all entries related to a quest"""
        return [e for e in self.entries if e.related_quest == quest_id]

    def get_npc_entries(self, npc_name: str) -> List[JournalEntry]:
        """Get all entries related to an NPC"""
        npc_lower = npc_name.lower()
        return [
            e
            for e in self.entries
            if e.related_npc and e.related_npc.lower() == npc_lower
        ]

    def clear_entries(self):
        """Clear all journal entries (for new adventure)"""
        self.entries.clear()
        self.next_entry_id = 1
        self.bookmarks.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize journal"""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "next_entry_id": self.next_entry_id,
            "map_annotations": {
                str(k): v.to_dict() for k, v in self.map_annotations.items()
            },
            "bookmarks": self.bookmarks,
            "auto_log_enabled": self.auto_log_enabled,
            "auto_log_combat": self.auto_log_combat,
            "auto_log_discoveries": self.auto_log_discoveries,
            "auto_log_conversations": self.auto_log_conversations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdventureJournal":
        """Deserialize journal"""
        journal = cls()
        journal.entries = [JournalEntry.from_dict(e) for e in data.get("entries", [])]
        journal.next_entry_id = data.get("next_entry_id", 1)
        journal.map_annotations = {
            int(k): MapAnnotation.from_dict(v)
            for k, v in data.get("map_annotations", {}).items()
        }
        journal.bookmarks = data.get("bookmarks", [])
        journal.auto_log_enabled = data.get("auto_log_enabled", True)
        journal.auto_log_combat = data.get("auto_log_combat", True)
        journal.auto_log_discoveries = data.get("auto_log_discoveries", True)
        journal.auto_log_conversations = data.get("auto_log_conversations", True)
        return journal
