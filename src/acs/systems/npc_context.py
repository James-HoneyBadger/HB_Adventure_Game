#!/usr/bin/env python3
"""
Adventure Construction Set - NPC Memory & Context System
Provides NPCs with memory, emotional states, and relationship tracking
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EmotionalState(Enum):
    """NPC emotional states that affect interactions"""

    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"
    HOSTILE = "hostile"
    AFRAID = "afraid"
    GRATEFUL = "grateful"
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"


class RelationshipLevel(Enum):
    """Player-NPC relationship levels"""

    ENEMY = -2
    DISLIKED = -1
    STRANGER = 0
    ACQUAINTANCE = 1
    FRIEND = 2
    TRUSTED = 3
    DEVOTED = 4


@dataclass
class ConversationMemory:
    """Tracks what has been discussed with an NPC"""

    topics_discussed: Set[str] = field(default_factory=set)
    questions_asked: Set[str] = field(default_factory=set)
    times_talked: int = 0
    last_conversation: Optional[datetime] = None
    revealed_secrets: Set[str] = field(default_factory=set)

    def add_topic(self, topic: str):
        """Record that a topic was discussed"""
        self.topics_discussed.add(topic.lower())

    def add_question(self, question: str):
        """Record a question that was asked"""
        self.questions_asked.add(question.lower())

    def has_discussed(self, topic: str) -> bool:
        """Check if a topic has been discussed"""
        return topic.lower() in self.topics_discussed

    def increment_conversation(self):
        """Record a conversation occurrence"""
        self.times_talked += 1
        self.last_conversation = datetime.now()


@dataclass
class NPCContext:
    """Complete context for an NPC including memory and emotional state"""

    npc_id: int
    name: str
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    relationship: RelationshipLevel = RelationshipLevel.STRANGER
    memory: ConversationMemory = field(default_factory=ConversationMemory)
    current_mood: str = "calm"
    trust_level: int = 50  # 0-100

    # Preferences and personality
    likes: List[str] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)

    # Quest and story state
    quest_state: Dict[str, Any] = field(default_factory=dict)
    custom_flags: Dict[str, bool] = field(default_factory=dict)

    def improve_relationship(self, amount: int = 1):
        """Improve relationship with the NPC"""
        self.trust_level = min(100, self.trust_level + amount * 10)

        # Update relationship level based on trust
        if self.trust_level >= 90:
            self.relationship = RelationshipLevel.DEVOTED
        elif self.trust_level >= 75:
            self.relationship = RelationshipLevel.TRUSTED
        elif self.trust_level >= 60:
            self.relationship = RelationshipLevel.FRIEND
        elif self.trust_level >= 40:
            self.relationship = RelationshipLevel.ACQUAINTANCE

    def damage_relationship(self, amount: int = 1):
        """Damage relationship with the NPC"""
        self.trust_level = max(0, self.trust_level - amount * 10)

        # Update relationship level
        if self.trust_level <= 10:
            self.relationship = RelationshipLevel.ENEMY
        elif self.trust_level <= 25:
            self.relationship = RelationshipLevel.DISLIKED
        elif self.trust_level <= 40:
            self.relationship = RelationshipLevel.STRANGER

    def set_emotion(self, emotion: EmotionalState):
        """Change the NPC's current emotional state"""
        self.emotional_state = emotion

        # Update mood description
        mood_map = {
            EmotionalState.FRIENDLY: "welcoming",
            EmotionalState.NEUTRAL: "calm",
            EmotionalState.SUSPICIOUS: "wary",
            EmotionalState.HOSTILE: "aggressive",
            EmotionalState.AFRAID: "fearful",
            EmotionalState.GRATEFUL: "appreciative",
            EmotionalState.ANGRY: "furious",
            EmotionalState.SAD: "melancholy",
            EmotionalState.HAPPY: "cheerful",
        }
        self.current_mood = mood_map.get(emotion, "calm")

    def get_dialogue_modifier(self) -> str:
        """Get a description of how the NPC speaks based on their state"""
        modifiers = {
            EmotionalState.FRIENDLY: "warmly",
            EmotionalState.NEUTRAL: "calmly",
            EmotionalState.SUSPICIOUS: "cautiously",
            EmotionalState.HOSTILE: "angrily",
            EmotionalState.AFRAID: "nervously",
            EmotionalState.GRATEFUL: "thankfully",
            EmotionalState.ANGRY: "furiously",
            EmotionalState.SAD: "sadly",
            EmotionalState.HAPPY: "cheerfully",
        }
        return modifiers.get(self.emotional_state, "")

    def should_remember_player(self) -> bool:
        """Check if NPC should recognize the player"""
        return self.memory.times_talked > 0

    def get_greeting(self) -> str:
        """Get appropriate greeting based on relationship and memory"""
        if not self.should_remember_player():
            return f"{self.name} looks at you curiously."

        greetings = {
            RelationshipLevel.DEVOTED: f"{self.name} greets you like an old friend!",
            RelationshipLevel.TRUSTED: f"{self.name} smiles warmly at you.",
            RelationshipLevel.FRIEND: f"{self.name} nods in recognition.",
            RelationshipLevel.ACQUAINTANCE: f"{self.name} acknowledges your presence.",
            RelationshipLevel.STRANGER: f"{self.name} regards you neutrally.",
            RelationshipLevel.DISLIKED: f"{self.name} frowns at your approach.",
            RelationshipLevel.ENEMY: f"{self.name} glares at you with hatred!",
        }

        return greetings.get(self.relationship, f"{self.name} looks at you.")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "emotional_state": self.emotional_state.value,
            "relationship": self.relationship.value,
            "current_mood": self.current_mood,
            "trust_level": self.trust_level,
            "topics_discussed": list(self.memory.topics_discussed),
            "questions_asked": list(self.memory.questions_asked),
            "times_talked": self.memory.times_talked,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "personality_traits": self.personality_traits,
            "quest_state": self.quest_state,
            "custom_flags": self.custom_flags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NPCContext":
        """Deserialize from dictionary"""
        memory = ConversationMemory(
            topics_discussed=set(data.get("topics_discussed", [])),
            questions_asked=set(data.get("questions_asked", [])),
            times_talked=data.get("times_talked", 0),
        )

        return cls(
            npc_id=data["npc_id"],
            name=data["name"],
            emotional_state=EmotionalState(data.get("emotional_state", "neutral")),
            relationship=RelationshipLevel(data.get("relationship", 0)),
            memory=memory,
            current_mood=data.get("current_mood", "calm"),
            trust_level=data.get("trust_level", 50),
            likes=data.get("likes", []),
            dislikes=data.get("dislikes", []),
            personality_traits=data.get("personality_traits", []),
            quest_state=data.get("quest_state", {}),
            custom_flags=data.get("custom_flags", {}),
        )


class NPCContextManager:
    """Manages context for all NPCs in the game"""

    def __init__(self):
        self.npc_contexts: Dict[int, NPCContext] = {}

    def get_or_create_context(self, npc_id: int, npc_name: str) -> NPCContext:
        """Get existing context or create new one for NPC"""
        if npc_id not in self.npc_contexts:
            self.npc_contexts[npc_id] = NPCContext(npc_id=npc_id, name=npc_name)
        return self.npc_contexts[npc_id]

    def get_context(self, npc_id: int) -> Optional[NPCContext]:
        """Get context for NPC if it exists"""
        return self.npc_contexts.get(npc_id)

    def record_conversation(self, npc_id: int, topic: str):
        """Record that player talked to NPC about topic"""
        if npc_id in self.npc_contexts:
            self.npc_contexts[npc_id].memory.add_topic(topic)
            self.npc_contexts[npc_id].memory.increment_conversation()

    def has_discussed_topic(self, npc_id: int, topic: str) -> bool:
        """Check if player has discussed topic with NPC"""
        context = self.get_context(npc_id)
        return context.memory.has_discussed(topic) if context else False

    def set_npc_emotion(self, npc_id: int, emotion: EmotionalState):
        """Set emotional state for NPC"""
        if npc_id in self.npc_contexts:
            self.npc_contexts[npc_id].set_emotion(emotion)

    def improve_relationship(self, npc_id: int, amount: int = 1):
        """Improve player's relationship with NPC"""
        if npc_id in self.npc_contexts:
            self.npc_contexts[npc_id].improve_relationship(amount)

    def damage_relationship(self, npc_id: int, amount: int = 1):
        """Damage player's relationship with NPC"""
        if npc_id in self.npc_contexts:
            self.npc_contexts[npc_id].damage_relationship(amount)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all NPC contexts"""
        return {
            str(npc_id): context.to_dict()
            for npc_id, context in self.npc_contexts.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NPCContextManager":
        """Deserialize NPC contexts"""
        manager = cls()
        for npc_id_str, context_data in data.items():
            npc_id = int(npc_id_str)
            manager.npc_contexts[npc_id] = NPCContext.from_dict(context_data)
        return manager
