#!/usr/bin/env python3
"""
Adventure Construction Set Launcher
Main menu system for selecting and playing adventures
"""

import os
import sys
import json
from pathlib import Path


class AdventureLauncher:
    """Main launcher for adventures"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.adventures_dir = self.base_dir / "adventures"
        self.adventures = []

    def discover_adventures(self):
        """Find all available adventure files"""
        if not self.adventures_dir.exists():
            print("No adventures directory found!")
            return

        self.adventures = []
        for json_file in self.adventures_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    self.adventures.append(
                        {
                            "file": json_file,
                            "title": data.get("title", "Untitled"),
                            "author": data.get("author", "Unknown"),
                            "intro": data.get("intro", ""),
                        }
                    )
            except (json.JSONDecodeError, IOError):
                continue

    def show_banner(self):
        """Display Adventure Construction Set banner"""
        print("\n" + "=" * 70)
        print(
            """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         ADVENTURE CONSTRUCTION SET                        ║
    ║         Build Your Own Text Adventures                    ║
    ║                                                           ║
    ║         Powered by Honey Badger Universe                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝   
 ██╔══╝  ██╔══██║██║╚██╔╝██║██║   ██║██║╚██╗██║
 ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
 ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
        """
        )
        print("         WONDERFUL WORLD OF EAMON - LINUX EDITION")
        print("=" * 70)

    def show_menu(self):
        """Display adventure selection menu"""
        print("\nAvailable Adventures:\n")

        if not self.adventures:
            print("No adventures found in the adventures directory!")
            print("Please add adventure JSON files to:", self.adventures_dir)
            return False

        for i, adv in enumerate(self.adventures, 1):
            print(f"{i}. {adv['title']}")
            if adv["author"] != "Unknown":
                print(f"   by {adv['author']}")

        print(f"\n{len(self.adventures) + 1}. Exit")
        return True

    def run(self):
        """Main launcher loop"""
        self.show_banner()
        self.discover_adventures()

        while True:
            if not self.show_menu():
                break

            try:
                choice = input("\nSelect an adventure (number): ").strip()

                if not choice.isdigit():
                    print("Please enter a number.")
                    continue

                choice_num = int(choice)

                if choice_num == len(self.adventures) + 1:
                    print("\nFarewell, adventurer!")
                    break

                if 1 <= choice_num <= len(self.adventures):
                    adventure = self.adventures[choice_num - 1]
                    self.launch_adventure(adventure["file"])
                else:
                    print("Invalid selection.")

            except KeyboardInterrupt:
                print("\n\nFarewell, adventurer!")
                break
            except ValueError:
                print("Please enter a valid number.")

    def launch_adventure(self, adventure_file):
        """Launch a specific adventure"""
        engine_path = self.base_dir / "acs_engine.py"

        if not engine_path.exists():
            print(f"Error: Game engine not found at {engine_path}")
            return

        print("\n" + "=" * 70)
        print("Loading adventure...")
        print("=" * 70)

        # Import and run the game engine
        import importlib.util

        spec = importlib.util.spec_from_file_location("acs_engine", engine_path)
        acs_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acs_module)

        # Create and run game
        game = acs_module.EamonGame(str(adventure_file))
        game.run()

        print("\n" + "=" * 70)
        print("Adventure completed. Returning to main menu...")
        print("=" * 70)


def main():
    """Entry point"""
    launcher = AdventureLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
