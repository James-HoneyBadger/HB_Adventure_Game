"""
Base plugin system for extensible game features

All game systems should inherit from BasePlugin to ensure
consistent initialization, lifecycle management, and event handling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Optional, Set


class PluginPriority(IntEnum):
    """Plugin initialization and event processing order"""

    CRITICAL = 0  # Core systems (state, IO)
    HIGH = 10  # Game logic (combat, items)
    NORMAL = 50  # Features (achievements, journal)
    LOW = 100  # UI/UX (tutorial, accessibility)


@dataclass
class PluginMetadata:
    """Plugin identification and configuration"""

    name: str
    version: str
    author: str = "ACS Team"
    description: str = ""
    dependencies: List[str] = None
    priority: PluginPriority = PluginPriority.NORMAL
    enabled: bool = True

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class BasePlugin(ABC):
    """
    Base class for all game system plugins

    Plugins provide modular, extensible functionality to the game engine.
    They follow a standard lifecycle and can communicate via events.

    Lifecycle:
        1. __init__() - Create instance
        2. initialize(state, event_bus, services) - Setup with dependencies
        3. on_enable() - Called when plugin activates
        4. ... game runs, handle events ...
        5. on_disable() - Called when plugin deactivates
        6. shutdown() - Cleanup resources
    """

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self._initialized = False
        self._enabled = metadata.enabled
        self.state = None
        self.event_bus = None
        self.services = None

    @abstractmethod
    def initialize(
        self, state: "GameState", event_bus: "EventBus", services: "ServiceRegistry"
    ):
        """
        Initialize plugin with engine dependencies

        Args:
            state: Centralized game state
            event_bus: Event communication system
            services: Shared service registry
        """
        self.state = state
        self.event_bus = event_bus
        self.services = services
        self._initialized = True

    @abstractmethod
    def get_event_subscriptions(self) -> Dict[str, callable]:
        """
        Return map of event names to handler methods

        Returns:
            Dict mapping event names to handler callables

        Example:
            {
                'game.move': self.on_move,
                'combat.start': self.on_combat_start,
            }
        """
        return {}

    def on_enable(self):
        """Called when plugin is enabled (override if needed)"""
        pass

    def on_disable(self):
        """Called when plugin is disabled (override if needed)"""
        pass

    def shutdown(self):
        """Cleanup resources before engine stops (override if needed)"""
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if plugin has been initialized"""
        return self._initialized

    @property
    def is_enabled(self) -> bool:
        """Check if plugin is currently enabled"""
        return self._enabled

    def enable(self):
        """Enable this plugin"""
        if not self._enabled:
            self._enabled = True
            self.on_enable()

    def disable(self):
        """Disable this plugin"""
        if self._enabled:
            self._enabled = False
            self.on_disable()

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get plugin configuration value

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        if self.services:
            config_service = self.services.get("config")
            if config_service:
                return config_service.get_plugin_config(
                    self.metadata.name, key, default
                )
        return default

    def set_config(self, key: str, value: Any):
        """
        Set plugin configuration value

        Args:
            key: Configuration key
            value: Value to set
        """
        if self.services:
            config_service = self.services.get("config")
            if config_service:
                config_service.set_plugin_config(self.metadata.name, key, value)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"'{self.metadata.name}' v{self.metadata.version}>"
        )
