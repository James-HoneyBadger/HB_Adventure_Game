"""
Event-driven communication system for loose coupling between plugins

The EventBus allows plugins to communicate without direct dependencies,
making the system more modular and easier to extend.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional
import logging


class EventPriority(IntEnum):
    """Event handler priority (lower values run first)"""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100


@dataclass
class Event:
    """
    Event data container

    Attributes:
        name: Event identifier (e.g., 'game.move', 'combat.hit')
        data: Event payload
        source: Plugin or system that emitted the event
        cancellable: Whether event can be cancelled
        cancelled: Whether event has been cancelled
    """

    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    cancellable: bool = False
    cancelled: bool = False

    def cancel(self):
        """Cancel this event (if cancellable)"""
        if self.cancellable:
            self.cancelled = True

    def is_cancelled(self) -> bool:
        """Check if event is cancelled"""
        return self.cancelled


@dataclass
class EventSubscription:
    """Event handler registration"""

    event_name: str
    handler: Callable[[Event], None]
    priority: EventPriority
    plugin_name: str

    def __lt__(self, other):
        """Sort by priority"""
        return self.priority < other.priority


class EventBus:
    """
    Central event bus for plugin communication

    Supports:
    - Event publishing/subscribing
    - Priority-based handler ordering
    - Event cancellation
    - Wildcard subscriptions
    - Event history/logging
    """

    def __init__(self, enable_history: bool = False):
        self.logger = logging.getLogger("EventBus")
        self._subscriptions: Dict[str, List[EventSubscription]] = {}
        self._wildcard_subscriptions: List[EventSubscription] = []
        self._enable_history = enable_history
        self._event_history: List[Event] = []

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        plugin_name: str = "unknown",
    ):
        """
        Subscribe to an event

        Args:
            event_name: Event to listen for (or '*' for all events)
            handler: Callable that receives Event objects
            priority: Handler execution priority
            plugin_name: Name of subscribing plugin
        """
        subscription = EventSubscription(
            event_name=event_name,
            handler=handler,
            priority=priority,
            plugin_name=plugin_name,
        )

        if event_name == "*":
            self._wildcard_subscriptions.append(subscription)
            self._wildcard_subscriptions.sort()
        else:
            if event_name not in self._subscriptions:
                self._subscriptions[event_name] = []
            self._subscriptions[event_name].append(subscription)
            self._subscriptions[event_name].sort()

        self.logger.debug(f"Subscribed {plugin_name} to {event_name}")

    def unsubscribe(self, event_name: str, handler: Callable):
        """
        Unsubscribe from an event

        Args:
            event_name: Event name
            handler: Handler to remove
        """
        if event_name == "*":
            self._wildcard_subscriptions = [
                sub for sub in self._wildcard_subscriptions if sub.handler != handler
            ]
        elif event_name in self._subscriptions:
            self._subscriptions[event_name] = [
                sub for sub in self._subscriptions[event_name] if sub.handler != handler
            ]

    def publish(
        self,
        event_name: str,
        data: Dict[str, Any] = None,
        source: str = "system",
        cancellable: bool = False,
    ) -> Event:
        """
        Publish an event to all subscribers

        Args:
            event_name: Event identifier
            data: Event payload
            source: Event source
            cancellable: Whether handlers can cancel the event

        Returns:
            Event object (check event.is_cancelled())
        """
        if data is None:
            data = {}

        event = Event(
            name=event_name, data=data, source=source, cancellable=cancellable
        )

        if self._enable_history:
            self._event_history.append(event)

        # Get specific and wildcard handlers
        handlers = []
        if event_name in self._subscriptions:
            handlers.extend(self._subscriptions[event_name])
        handlers.extend(self._wildcard_subscriptions)
        handlers.sort()

        # Execute handlers in priority order
        for subscription in handlers:
            if event.is_cancelled():
                break

            try:
                subscription.handler(event)
            except Exception as e:
                self.logger.error(
                    f"Error in {subscription.plugin_name} "
                    f"handling {event_name}: {e}"
                )

        return event

    def get_subscriptions(self, event_name: str) -> List[str]:
        """Get list of plugins subscribed to an event"""
        plugins = []
        if event_name in self._subscriptions:
            plugins.extend([s.plugin_name for s in self._subscriptions[event_name]])
        return plugins

    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()

    def get_history(
        self, event_name: Optional[str] = None, limit: int = 100
    ) -> List[Event]:
        """
        Get recent event history

        Args:
            event_name: Filter by event name (None for all)
            limit: Maximum events to return

        Returns:
            List of recent events
        """
        if not self._enable_history:
            return []

        history = self._event_history
        if event_name:
            history = [e for e in history if e.name == event_name]

        return history[-limit:]

    def clear_all_subscriptions(self):
        """Remove all subscriptions (useful for testing)"""
        self._subscriptions.clear()
        self._wildcard_subscriptions.clear()
