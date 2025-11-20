"""
I/O service for file operations and data persistence
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from core.services import Service


class IOService(Service):
    """
    Handles all file I/O operations

    Provides:
    - Adventure loading/saving
    - Save game management
    - JSON file operations
    - Path management
    """

    def __init__(self, base_dir: str = "."):
        self.logger = logging.getLogger("IOService")
        self.base_dir = Path(base_dir)
        self.adventures_dir = self.base_dir / "adventures"
        self.saves_dir = self.base_dir / "saves"

    def initialize(self, config: Dict[str, Any]):
        """Initialize the I/O service"""
        # Create directories
        self.adventures_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        # Override paths from config
        if "adventures_dir" in config:
            self.adventures_dir = Path(config["adventures_dir"])
        if "saves_dir" in config:
            self.saves_dir = Path(config["saves_dir"])

        self.logger.info("I/O service initialized")

    def shutdown(self):
        """Cleanup (nothing needed for basic I/O)"""
        pass

    def load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load JSON file

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data or None on error
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return None

    def save_json(self, file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
        """
        Save data to JSON file

        Args:
            file_path: Path to save to
            data: Data to save
            indent: JSON indentation

        Returns:
            True on success, False on error
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=indent)
            return True
        except Exception as e:
            self.logger.error(f"Error saving to {file_path}: {e}")
            return False

    def load_adventure(self, adventure_name: str) -> Optional[Dict[str, Any]]:
        """
        Load an adventure by name

        Args:
            adventure_name: Name of adventure (without .json)

        Returns:
            Adventure data or None
        """
        adventure_path = self.adventures_dir / f"{adventure_name}.json"
        return self.load_json(adventure_path)

    def list_adventures(self) -> list:
        """List available adventures"""
        if not self.adventures_dir.exists():
            return []
        return [f.stem for f in self.adventures_dir.glob("*.json")]

    def save_game(self, save_name: str, game_state: Dict[str, Any]) -> bool:
        """
        Save game state

        Args:
            save_name: Name for the save file
            game_state: State data to save

        Returns:
            True on success
        """
        save_path = self.saves_dir / f"{save_name}.json"
        return self.save_json(save_path, game_state)

    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Load saved game

        Args:
            save_name: Name of save file

        Returns:
            Saved state or None
        """
        save_path = self.saves_dir / f"{save_name}.json"
        return self.load_json(save_path)

    def list_saves(self) -> list:
        """List available save files"""
        if not self.saves_dir.exists():
            return []
        return [f.stem for f in self.saves_dir.glob("*.json")]

    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        save_path = self.saves_dir / f"{save_name}.json"
        try:
            save_path.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting save {save_name}: {e}")
            return False
