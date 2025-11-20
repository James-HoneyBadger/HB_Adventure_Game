#!/usr/bin/env python3
"""
Eamon DSK to JSON Converter
Extracts adventure data from Apple II .DSK disk images and converts to JSON
format compatible with the Linux Eamon engine.

Supports:
- DOS 3.3 disk images (.dsk, .do)
- Eamon adventure data files
- EAMON.DESC, EAMON.ROOM, EAMON.ARTIFACT, EAMON.EFFECT, EAMON.MONSTER files
"""

import struct
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class DOS33DiskImage:
    """Parser for Apple II DOS 3.3 disk images"""

    SECTOR_SIZE = 256
    TRACKS = 35
    SECTORS_PER_TRACK = 16

    # DOS 3.3 sector interleaving
    SECTOR_INTERLEAVE = [
        0x0,
        0x7,
        0xE,
        0x6,
        0xD,
        0x5,
        0xC,
        0x4,
        0xB,
        0x3,
        0xA,
        0x2,
        0x9,
        0x1,
        0x8,
        0xF,
    ]

    def __init__(self, filename: str):
        self.filename = filename
        self.data = bytearray()
        self.vtoc_track = 17
        self.vtoc_sector = 0
        self.catalog_track = 17
        self.catalog_sector = 1
        self.files = {}

    def load(self):
        """Load disk image into memory"""
        try:
            with open(self.filename, "rb") as f:
                self.data = bytearray(f.read())

            expected_size = self.TRACKS * self.SECTORS_PER_TRACK * self.SECTOR_SIZE

            if len(self.data) < expected_size:
                print(
                    f"Warning: Disk image smaller than expected "
                    f"({len(self.data)} < {expected_size})"
                )

            return True
        except IOError as e:
            print(f"Error loading disk image: {e}")
            return False

    def read_sector(self, track: int, sector: int) -> bytearray:
        """Read a sector from the disk image"""
        if track >= self.TRACKS or sector >= self.SECTORS_PER_TRACK:
            return bytearray(self.SECTOR_SIZE)

        offset = (track * self.SECTORS_PER_TRACK + sector) * self.SECTOR_SIZE
        return self.data[offset : offset + self.SECTOR_SIZE]

    def read_catalog(self) -> Dict[str, Dict]:
        """Read the DOS 3.3 catalog and extract file information"""
        files = {}
        track = self.catalog_track
        sector = self.catalog_sector

        while track != 0:
            sector_data = self.read_sector(track, sector)

            # Next catalog sector
            next_track = sector_data[1]
            next_sector = sector_data[2]

            # Process file entries (7 per catalog sector, starting at offset 11)
            for i in range(7):
                offset = 11 + (i * 35)

                # First byte is track of first file sector (0 = deleted)
                first_track = sector_data[offset]
                if first_track == 0 or first_track == 0xFF:
                    continue

                first_sector = sector_data[offset + 1]
                file_type = sector_data[offset + 2]

                # Filename is 30 bytes starting at offset + 3
                filename_bytes = sector_data[offset + 3 : offset + 33]
                filename = self._decode_filename(filename_bytes)

                # File length in sectors
                length = sector_data[offset + 33] + (sector_data[offset + 34] << 8)

                files[filename] = {
                    "type": file_type,
                    "track": first_track,
                    "sector": first_sector,
                    "length": length,
                    "filename": filename,
                }

            if next_track == 0:
                break

            track = next_track
            sector = next_sector

        self.files = files
        return files

    def _decode_filename(self, data: bytearray) -> str:
        """Decode DOS 3.3 filename (high-bit ASCII)"""
        name = ""
        for byte in data:
            if byte == 0x00 or byte == 0xA0:  # Null or space padding
                break
            char = byte & 0x7F  # Strip high bit
            if 32 <= char <= 126:
                name += chr(char)
        return name.strip()

    def read_file(self, filename: str) -> Optional[bytearray]:
        """Read a file from the disk image"""
        if filename not in self.files:
            return None

        file_info = self.files[filename]
        track = file_info["track"]
        sector = file_info["sector"]

        data = bytearray()
        visited = set()

        while track != 0 and (track, sector) not in visited:
            visited.add((track, sector))
            sector_data = self.read_sector(track, sector)

            # Track/sector list format:
            # Byte 1: next track
            # Byte 2: next sector
            # Bytes 12+: offset pairs for data sectors
            next_track = sector_data[1]
            next_sector = sector_data[2]

            # Read data sectors referenced in this T/S list
            for i in range(12, 256, 2):
                data_track = sector_data[i]
                data_sector = sector_data[i + 1]

                if data_track == 0:
                    break

                data_sector_content = self.read_sector(data_track, data_sector)
                data.extend(data_sector_content)

            track = next_track
            sector = next_sector

        return data


class EamonDataReader:
    """Reader for Eamon data files"""

    def __init__(self):
        self.rooms = []
        self.artifacts = []
        self.effects = []
        self.monsters = []
        self.description = {}

    def read_integer(self, data: bytearray, offset: int) -> Tuple[int, int]:
        """Read an Applesoft BASIC integer (2 bytes, little endian)"""
        if offset + 1 >= len(data):
            return 0, offset + 2
        value = data[offset] + (data[offset + 1] << 8)
        # Handle signed integers
        if value >= 32768:
            value -= 65536
        return value, offset + 2

    def read_string(self, data: bytearray, offset: int, length: int) -> Tuple[str, int]:
        """Read a string from data"""
        if offset + length > len(data):
            return "", offset + length

        text = ""
        for i in range(length):
            byte = data[offset + i]
            if byte == 0:
                break
            # Handle high-bit ASCII
            char = byte & 0x7F
            if 32 <= char <= 126:
                text += chr(char)

        return text.strip(), offset + length

    def read_description_file(self, data: bytearray) -> Dict:
        """Read EAMON.DESC file"""
        desc = {"title": "", "author": "", "version": "", "intro": ""}

        # Skip Applesoft BASIC header if present
        offset = 0

        # Try to find text data
        # Eamon descriptions are typically stored as strings
        text = ""
        for byte in data:
            if byte == 0:
                continue
            char = byte & 0x7F
            if 32 <= char <= 126 or char == 13:  # Printable or CR
                if char == 13:
                    text += "\n"
                else:
                    text += chr(char)

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if len(lines) > 0:
            desc["title"] = lines[0]
        if len(lines) > 1:
            desc["author"] = lines[1]
        if len(lines) > 2:
            desc["intro"] = "\n".join(lines[2:])

        return desc

    def read_room_file(self, data: bytearray) -> List[Dict]:
        """Read EAMON.ROOM file"""
        rooms = []

        # Eamon room records are typically ~100 bytes each
        # Format varies, but generally:
        # - Room number (2 bytes)
        # - Name (40 bytes)
        # - Description (variable)
        # - Exits (12 bytes, 2 per direction)

        offset = 0
        room_id = 1

        # Simple parser - read in chunks
        while offset < len(data) - 100:
            room = {
                "id": room_id,
                "name": "",
                "description": "",
                "exits": {},
                "is_dark": False,
            }

            # Try to extract room name (typically first string)
            name, offset = self.read_string(data, offset, 40)
            if name:
                room["name"] = name

            # Try to extract description
            desc, offset = self.read_string(data, offset, 200)
            if desc:
                room["description"] = desc

            # Try to read exits (N, S, E, W, U, D)
            exits = {}
            for direction in ["north", "south", "east", "west", "up", "down"]:
                exit_room, offset = self.read_integer(data, offset)
                if exit_room > 0 and exit_room < 200:
                    exits[direction] = exit_room

            room["exits"] = exits

            if room["name"] or room["description"]:
                rooms.append(room)
                room_id += 1

            # Skip to next potential record
            if offset >= len(data) - 100:
                break

        return rooms

    def read_artifact_file(self, data: bytearray) -> List[Dict]:
        """Read EAMON.ARTIFACT (items) file"""
        artifacts = []

        # Eamon artifact records contain:
        # - ID, Name, Description
        # - Weight, Value, Type
        # - Weapon/Armor stats
        # - Location

        offset = 0
        item_id = 1

        while offset < len(data) - 50:
            item = {
                "id": item_id,
                "name": "",
                "description": "",
                "type": "normal",
                "weight": 1,
                "value": 0,
                "is_weapon": False,
                "weapon_type": 0,
                "weapon_dice": 1,
                "weapon_sides": 6,
                "is_armor": False,
                "armor_value": 0,
                "is_takeable": True,
                "location": 0,
            }

            # Read name
            name, offset = self.read_string(data, offset, 40)
            if name:
                item["name"] = name

            # Read description
            desc, offset = self.read_string(data, offset, 100)
            if desc:
                item["description"] = desc

            # Read stats
            weight, offset = self.read_integer(data, offset)
            value, offset = self.read_integer(data, offset)
            location, offset = self.read_integer(data, offset)

            item["weight"] = max(1, weight) if weight > 0 else 1
            item["value"] = max(0, value) if value >= 0 else 0
            item["location"] = location

            if item["name"]:
                artifacts.append(item)
                item_id += 1

            if offset >= len(data) - 50:
                break

        return artifacts

    def read_monster_file(self, data: bytearray) -> List[Dict]:
        """Read EAMON.MONSTER file"""
        monsters = []

        # Eamon monster records:
        # - ID, Name, Description
        # - Hardiness, Agility, Charisma
        # - Friendliness, Courage
        # - Weapon, Armor
        # - Room location

        offset = 0
        monster_id = 1

        while offset < len(data) - 60:
            monster = {
                "id": monster_id,
                "name": "",
                "description": "",
                "room_id": 1,
                "hardiness": 10,
                "agility": 10,
                "friendliness": "neutral",
                "courage": 100,
                "weapon_id": None,
                "armor_worn": 0,
                "gold": 0,
            }

            # Read name
            name, offset = self.read_string(data, offset, 40)
            if name:
                monster["name"] = name

            # Read description
            desc, offset = self.read_string(data, offset, 100)
            if desc:
                monster["description"] = desc

            # Read stats
            hardiness, offset = self.read_integer(data, offset)
            agility, offset = self.read_integer(data, offset)
            room_id, offset = self.read_integer(data, offset)

            monster["hardiness"] = max(1, hardiness) if hardiness > 0 else 10
            monster["agility"] = max(1, agility) if agility > 0 else 10
            monster["room_id"] = room_id if room_id > 0 else 1

            if monster["name"]:
                monsters.append(monster)
                monster_id += 1

            if offset >= len(data) - 60:
                break

        return monsters


class EamonConverter:
    """Main converter class"""

    def __init__(self, dsk_file: str):
        self.dsk_file = dsk_file
        self.disk = DOS33DiskImage(dsk_file)
        self.reader = EamonDataReader()

    def convert(self, output_file: str = None) -> Dict:
        """Convert Eamon DSK to JSON format"""
        print(f"Loading disk image: {self.dsk_file}")

        if not self.disk.load():
            print("Failed to load disk image")
            return None

        print("Reading catalog...")
        files = self.disk.read_catalog()

        print(f"Found {len(files)} files on disk:")
        for filename in sorted(files.keys()):
            print(f"  - {filename}")

        # Initialize adventure data
        adventure = {
            "title": "Untitled Eamon Adventure",
            "author": "Unknown",
            "intro": "",
            "start_room": 1,
            "rooms": [],
            "items": [],
            "monsters": [],
            "effects": [],
        }

        # Read description file
        desc_files = ["EAMON.DESC", "EAMON DESC", "DESC"]
        for desc_file in desc_files:
            if desc_file in files:
                print(f"\nReading {desc_file}...")
                data = self.disk.read_file(desc_file)
                if data:
                    desc = self.reader.read_description_file(data)
                    adventure.update(desc)
                    print(f"  Title: {desc.get('title', 'N/A')}")
                    print(f"  Author: {desc.get('author', 'N/A')}")
                break

        # Read room file
        room_files = ["EAMON.ROOM", "EAMON ROOM", "ROOM", "ROOMS"]
        for room_file in room_files:
            if room_file in files:
                print(f"\nReading {room_file}...")
                data = self.disk.read_file(room_file)
                if data:
                    rooms = self.reader.read_room_file(data)
                    adventure["rooms"] = rooms
                    print(f"  Found {len(rooms)} rooms")
                break

        # Read artifact file
        artifact_files = ["EAMON.ARTIFACT", "EAMON ARTIFACT", "ARTIFACT", "ARTIFACTS"]
        for artifact_file in artifact_files:
            if artifact_file in files:
                print(f"\nReading {artifact_file}...")
                data = self.disk.read_file(artifact_file)
                if data:
                    artifacts = self.reader.read_artifact_file(data)
                    adventure["items"] = artifacts
                    print(f"  Found {len(artifacts)} items")
                break

        # Read monster file
        monster_files = ["EAMON.MONSTER", "EAMON MONSTER", "MONSTER", "MONSTERS"]
        for monster_file in monster_files:
            if monster_file in files:
                print(f"\nReading {monster_file}...")
                data = self.disk.read_file(monster_file)
                if data:
                    monsters = self.reader.read_monster_file(data)
                    adventure["monsters"] = monsters
                    print(f"  Found {len(monsters)} monsters")
                break

        # Save to JSON
        if output_file:
            print(f"\nSaving to {output_file}...")
            with open(output_file, "w") as f:
                json.dump(adventure, f, indent=2)
            print("Conversion complete!")

        return adventure


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Eamon DSK to JSON Converter")
        print("=" * 60)
        print("\nUsage: dsk_converter.py <disk_image.dsk> [output.json]")
        print("\nExamples:")
        print("  dsk_converter.py adventure.dsk")
        print("  dsk_converter.py adventure.dsk my_adventure.json")
        print("\nThis tool extracts Eamon adventure data from Apple II")
        print("disk images and converts it to JSON format compatible")
        print("with the Linux Eamon engine.")
        sys.exit(1)

    dsk_file = sys.argv[1]

    if not os.path.exists(dsk_file):
        print(f"Error: File '{dsk_file}' not found")
        sys.exit(1)

    # Determine output filename
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base_name = Path(dsk_file).stem
        output_file = f"adventures/{base_name}.json"

    # Ensure adventures directory exists
    os.makedirs("adventures", exist_ok=True)

    # Convert
    converter = EamonConverter(dsk_file)
    result = converter.convert(output_file)

    if result:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nConverted adventure: {result.get('title', 'Unknown')}")
        print(f"Output file: {output_file}")
        print(f"\nTo play: ./play_adventure.sh {os.path.basename(output_file)}")
    else:
        print("\nConversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
