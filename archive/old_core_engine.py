"""
Main game engine orchestrator

The Engine coordinates all game systems, manages the game loop,
and handles plugin lifecycle.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base_plugin import BasePlugin, PluginPriority
from .event_bus import EventBus, EventPriority
from .game_state import GameState, GamePhase
from .services import ServiceRegistry


class Engine:
    """
    Main game engine

    Responsibilities:
    - Initialize and manage plugins
    - Coordinate the game loop
    - Manage game state transitions
    - Provide plugin discovery and loading

    Usage:
        engine = Engine()
        engine.register_plugin(MyPlugin())
        engine.initialize()
        engine.load_adventure('my_adventure.json')
        engine.run()
    """

    def __init__(self, enable_event_history: bool = False):
        self.logger = logging.getLogger("Engine")
        self.state = GameState()
        self.event_bus = EventBus(enable_history=enable_event_history)
        self.services = ServiceRegistry()

        self._plugins: Dict[str, BasePlugin] = {}
        self._plugins_by_priority: List[BasePlugin] = []
        self._initialized = False
        self._running = False

    def register_plugin(self, plugin: BasePlugin):
        """
        Register a plugin with the engine

        Args:
            plugin: Plugin instance to register
        """
        name = plugin.metadata.name

        if name in self._plugins:
            self.logger.warning(f"Plugin '{name}' already registered, replacing")

        self._plugins[name] = plugin
        self.logger.info(f"Registered plugin: {name} v{plugin.metadata.version}")

        # Rebuild priority list
        self._plugins_by_priority = sorted(
            self._plugins.values(), key=lambda p: p.metadata.priority
        )

    def unregister_plugin(self, plugin_name: str):
        """
        Unregister a plugin

        Args:
            plugin_name: Name of plugin to remove
        """
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            if plugin.is_initialized:
                plugin.shutdown()
            del self._plugins[plugin_name]
            self._plugins_by_priority.remove(plugin)
            self.logger.info(f"Unregistered plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name"""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> List[str]:
        """Get list of registered plugin names"""
        return list(self._plugins.keys())

    def initialize(self):
        """
        Initialize the engine and all plugins

        Plugins are initialized in priority order.
        Each plugin receives the state, event bus, and services.
        """
        if self._initialized:
            self.logger.warning("Engine already initialized")
            return

        self.logger.info("Initializing engine...")

        # Initialize plugins in priority order
        for plugin in self._plugins_by_priority:
            try:
                self.logger.debug(f"Initializing {plugin.metadata.name}...")
                plugin.initialize(self.state, self.event_bus, self.services)

                # Subscribe to events
                subscriptions = plugin.get_event_subscriptions()
                for event_name, handler in subscriptions.items():
                    self.event_bus.subscribe(
                        event_name=event_name,
                        handler=handler,
                        priority=EventPriority(plugin.metadata.priority.value),
                        plugin_name=plugin.metadata.name,
                    )

                # Enable if configured
                if plugin.metadata.enabled:
                    plugin.enable()

            except Exception as e:
                self.logger.error(f"Failed to initialize {plugin.metadata.name}: {e}")
                raise

        self._initialized = True
        self.event_bus.publish("engine.initialized")
        self.logger.info("Engine initialized successfully")

    def load_adventure(self, adventure_path: str):
        """
        Load an adventure

        Args:
            adventure_path: Path to adventure JSON file
        """
        event = self.event_bus.publish(
            "adventure.load", {"path": adventure_path}, cancellable=True
        )

        if not event.is_cancelled():
            self.logger.info(f"Adventure loaded: {adventure_path}")
            self.state.phase = GamePhase.INTRO

    def process_command(self, command: str) -> bool:
        """
        Process a player command

        Args:
            command: Command string

        Returns:
            True if command was handled, False otherwise
        """
        event = self.event_bus.publish(
            "command.input", {"command": command, "handled": False}, cancellable=False
        )

        return event.data.get("handled", False)

    def run(self):
        """
        Run the main game loop

        This is a basic REPL loop. GUI applications should
        integrate differently.
        """
        if not self._initialized:
            raise RuntimeError("Engine not initialized. Call initialize() first.")

        self._running = True
        self.event_bus.publish("game.start")

        try:
            while self._running and self.state.phase != GamePhase.GAME_OVER:
                # Get player input
                try:
                    command = input("> ").strip()
                    if not command:
                        continue

                    # Process command
                    if command.lower() in ["quit", "exit", "q"]:
                        break

                    self.process_command(command)
                    self.state.increment_turn()

                except KeyboardInterrupt:
                    print("\nInterrupted by user")
                    break

        finally:
            self.shutdown()

    def stop(self):
        """Stop the game loop"""
        self._running = False

    def shutdown(self):
        """
        Shutdown the engine and all plugins

        Plugins are shut down in reverse priority order.
        """
        if not self._initialized:
            return

        self.logger.info("Shutting down engine...")
        self.event_bus.publish("game.shutdown")

        # Shutdown plugins in reverse order
        for plugin in reversed(self._plugins_by_priority):
            try:
                self.logger.debug(f"Shutting down {plugin.metadata.name}...")
                plugin.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down {plugin.metadata.name}: {e}")

        # Shutdown services
        self.services.shutdown_all()

        self._initialized = False
        self._running = False
        self.logger.info("Engine shut down")

    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"<Engine {status}, {len(self._plugins)} plugins>"
