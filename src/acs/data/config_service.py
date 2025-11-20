"""
Configuration service for managing game and plugin settings
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from core.services import Service

# YAML is optional
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None


class ConfigService(Service):
    """
    Manages configuration for the engine and plugins

    Supports:
    - Multiple config file formats (JSON, YAML)
    - Plugin-specific configurations
    - Default values
    - Config validation
    - Hot reloading
    """

    def __init__(self, config_dir: str = "config"):
        self.logger = logging.getLogger("ConfigService")
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}

    def initialize(self, config: Dict[str, Any]):
        """Initialize the config service"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load main config
        main_config_path = self.config_dir / "engine.yaml"
        if not main_config_path.exists():
            main_config_path = self.config_dir / "engine.json"

        if main_config_path.exists():
            self.load_config(main_config_path)
        else:
            self._config = config or {}
            self._save_default_config()

        # Load plugin configs
        self._load_plugin_configs()

    def shutdown(self):
        """Save all configurations"""
        self.save_all()

    def load_config(self, config_path: Path):
        """Load main configuration file"""
        try:
            with open(config_path, "r") as f:
                if config_path.suffix == ".yaml" and YAML_AVAILABLE:
                    self._config = yaml.safe_load(f) or {}
                else:
                    self._config = json.load(f)
            self.logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        parts = key.split(".")
        value = self._config

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any):
        """Set a configuration value"""
        parts = key.split(".")
        config = self._config

        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        config[parts[-1]] = value

    def get_plugin_config(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """Get plugin-specific configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}

        parts = key.split(".")
        value = self._plugin_configs[plugin_name]

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def set_plugin_config(self, plugin_name: str, key: str, value: Any):
        """Set plugin-specific configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}

        parts = key.split(".")
        config = self._plugin_configs[plugin_name]

        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        config[parts[-1]] = value

    def _load_plugin_configs(self):
        """Load all plugin configuration files"""
        plugins_dir = self.config_dir / "plugins"
        if not plugins_dir.exists():
            return

        for config_file in plugins_dir.glob("*.yaml"):
            plugin_name = config_file.stem
            try:
                with open(config_file, "r") as f:
                    self._plugin_configs[plugin_name] = yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Failed to load config for {plugin_name}: {e}")

        for config_file in plugins_dir.glob("*.json"):
            plugin_name = config_file.stem
            if plugin_name not in self._plugin_configs:
                try:
                    with open(config_file, "r") as f:
                        self._plugin_configs[plugin_name] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Failed to load config for {plugin_name}: {e}")

    def _save_default_config(self):
        """Save default engine configuration"""
        default_config = {
            "engine": {
                "name": "Adventure Construction Set",
                "version": "2.0",
                "enable_event_history": False,
            },
            "gameplay": {
                "auto_save": True,
                "save_interval": 5,
                "difficulty": "normal",
            },
            "ui": {
                "theme": "dark",
                "font_size": 12,
                "color_enabled": True,
            },
        }

        config_path = self.config_dir / "engine.json"
        try:
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            self._config = default_config
            self.logger.info("Created default config")
        except Exception as e:
            self.logger.error(f"Failed to save default config: {e}")

    def save_all(self):
        """Save all configurations to disk"""
        # Save main config
        config_path = self.config_dir / "engine.json"
        try:
            with open(config_path, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

        # Save plugin configs
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir(exist_ok=True)

        for plugin_name, config in self._plugin_configs.items():
            config_path = plugins_dir / f"{plugin_name}.json"
            try:
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
            except Exception as e:
                self.logger.error(f"Failed to save config for {plugin_name}: {e}")
