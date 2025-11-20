#!/usr/bin/env python3
"""
Clean up duplicate Eamon adventures, keeping only the best version of each.
Priority:
1. Keep newer dated versions over older ones
2. Keep Eamon Adventurer's Guild over Computer Learning Center Library
3. Remove [a] alternate versions if a primary version exists
4. Keep special versions (utility masters, specific features)
"""

import os
import re
from collections import defaultdict


def parse_filename(filename):
    """Extract adventure number and metadata from filename."""
    # Match pattern: Eamon Adventure #XXX - Title (date)(author)(tags)
    match = re.match(r"Eamon Adventure #(\d+[A-D]?)\s*-\s*(.+?)\.do$", filename)
    if not match:
        return None

    number = match.group(1)
    rest = match.group(2)

    # Extract date
    date_match = re.search(r"\((\d{4}(?:-\d{2}-\d{2})?|19xx)\)", rest)
    date = date_match.group(1) if date_match else "0000"

    # Check for alternate version marker [a]
    is_alternate = "[a]" in rest

    # Check for older Computer Learning Center version
    is_old_version = "Computer Learning Center Library" in rest

    # Check for special features
    is_special = any(
        marker in rest
        for marker in [
            "Eamon Utility Master",
            "DDD v",
            "req 80-col",
            "Single-Disk Version",
        ]
    )

    return {
        "filename": filename,
        "number": number,
        "date": date,
        "is_alternate": is_alternate,
        "is_old_version": is_old_version,
        "is_special": is_special,
        "rest": rest,
    }


def select_best_version(versions):
    """Select the best version to keep from a list of versions."""
    if len(versions) == 1:
        return versions

    # Sort by priority:
    # 1. Not alternate version
    # 2. Not old Computer Learning Center version
    # 3. Special versions get bonus
    # 4. Newer date
    def sort_key(v):
        date_val = 0
        if v["date"] != "19xx" and v["date"] != "0000":
            try:
                # Convert date to sortable number
                date_val = int(v["date"].replace("-", ""))
            except:
                date_val = 0

        return (
            not v["is_special"],  # Special first (False < True)
            v["is_alternate"],  # Primary first
            v["is_old_version"],  # Newer first
            -date_val,  # Newer date first
        )

    sorted_versions = sorted(versions, key=sort_key)

    # Keep the best one, and any special versions
    to_keep = [sorted_versions[0]]
    for v in sorted_versions[1:]:
        if v["is_special"] and not sorted_versions[0]["is_special"]:
            to_keep.append(v)

    return to_keep


def main():
    eamon_dir = "/home/james/HB_Adventure_Games/Eamon"

    # Group files by adventure number
    adventures = defaultdict(list)

    for filename in os.listdir(eamon_dir):
        if not filename.endswith(".do"):
            continue

        parsed = parse_filename(filename)
        if parsed:
            adventures[parsed["number"]].append(parsed)

    # Find files to delete
    to_delete = []
    to_keep = []

    for number, versions in sorted(adventures.items()):
        keep = select_best_version(versions)
        keep_filenames = {v["filename"] for v in keep}

        for v in versions:
            if v["filename"] in keep_filenames:
                to_keep.append(v["filename"])
            else:
                to_delete.append(v["filename"])

    # Display summary
    print(f"Total files: {sum(len(v) for v in adventures.values())}")
    print(f"Files to keep: {len(to_keep)}")
    print(f"Files to delete: {len(to_delete)}")
    print()

    if to_delete:
        print("Files to be deleted:")
        for f in sorted(to_delete):
            print(f"  {f}")
        print()

        response = input("Proceed with deletion? (yes/no): ")
        if response.lower() == "yes":
            for filename in to_delete:
                filepath = os.path.join(eamon_dir, filename)
                os.remove(filepath)
                print(f"Deleted: {filename}")
            print(f"\nDeleted {len(to_delete)} files")
        else:
            print("Cancelled")
    else:
        print("No duplicates found to delete")


if __name__ == "__main__":
    main()
