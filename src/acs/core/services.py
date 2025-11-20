"""
Service registry for shared utilities and dependencies

Services provide cross-cutting functionality like I/O, configuration,
and data access without tight coupling.
"""

from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
import logging


class Service(ABC):
    """
    Base class for services

    Services provide shared functionality to plugins without
    creating tight coupling. Examples: file I/O, database access,
    configuration management, logging.
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """Initialize service with configuration"""
        pass

    @abstractmethod
    def shutdown(self):
        """Cleanup resources"""
        pass


class ServiceRegistry:
    """
    Registry for managing shared services

    Services can be registered by name and retrieved by plugins.
    This enables dependency injection and easier testing.
    """

    def __init__(self):
        self.logger = logging.getLogger("ServiceRegistry")
        self._services: Dict[str, Service] = {}

    def register(self, name: str, service: Service):
        """
        Register a service

        Args:
            name: Service identifier
            service: Service instance
        """
        if name in self._services:
            self.logger.warning(f"Overwriting service '{name}'")
        self._services[name] = service
        self.logger.debug(f"Registered service '{name}'")

    def unregister(self, name: str):
        """
        Unregister a service

        Args:
            name: Service identifier
        """
        if name in self._services:
            del self._services[name]
            self.logger.debug(f"Unregistered service '{name}'")

    def get(self, name: str) -> Optional[Service]:
        """
        Get a service by name

        Args:
            name: Service identifier

        Returns:
            Service instance or None
        """
        return self._services.get(name)

    def has(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services

    def list_services(self) -> list:
        """Get list of registered service names"""
        return list(self._services.keys())

    def shutdown_all(self):
        """Shutdown all registered services"""
        for name, service in self._services.items():
            try:
                service.shutdown()
                self.logger.debug(f"Shut down service '{name}'")
            except Exception as e:
                self.logger.error(f"Error shutting down '{name}': {e}")
