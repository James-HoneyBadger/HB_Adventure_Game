#!/usr/bin/env python3
"""
Adventure Construction Set - Graphical Adventure Editor
A complete IDE for creating, editing, and playing text adventures
Compatible with classic Eamon format and Apple II DSK files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import subprocess
import sys
import importlib.util
from pathlib import Path
from io import StringIO


class AdventureIDE:
    """Main IDE window for Adventure Construction Set"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Adventure Construction Set - IDE")
        self.root.geometry("1400x900")

        # Theme definitions
        self.themes = {
            "Dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "accent": "#4a90e2",
                "accent_dark": "#357abd",
                "success": "#5cb85c",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "sidebar": "#3c3c3c",
                "panel": "#353535",
                "border": "#4a4a4a",
                "text_bg": "#252525",
                "button": "#4a90e2",
                "button_hover": "#357abd",
            },
            "Light": {
                "bg": "#f5f5f5",
                "fg": "#333333",
                "accent": "#4a90e2",
                "accent_dark": "#357abd",
                "success": "#5cb85c",
                "warning": "#f0ad4e",
                "danger": "#d9534f",
                "sidebar": "#e0e0e0",
                "panel": "#ffffff",
                "border": "#cccccc",
                "text_bg": "#ffffff",
                "button": "#4a90e2",
                "button_hover": "#357abd",
            },
            "Dracula": {
                "bg": "#282a36",
                "fg": "#f8f8f2",
                "accent": "#bd93f9",
                "accent_dark": "#9d73d9",
                "success": "#50fa7b",
                "warning": "#f1fa8c",
                "danger": "#ff5555",
                "sidebar": "#1e1f28",
                "panel": "#44475a",
                "border": "#6272a4",
                "text_bg": "#1e1f28",
                "button": "#bd93f9",
                "button_hover": "#9d73d9",
            },
            "Nord": {
                "bg": "#2e3440",
                "fg": "#eceff4",
                "accent": "#88c0d0",
                "accent_dark": "#5e81ac",
                "success": "#a3be8c",
                "warning": "#ebcb8b",
                "danger": "#bf616a",
                "sidebar": "#3b4252",
                "panel": "#434c5e",
                "border": "#4c566a",
                "text_bg": "#2e3440",
                "button": "#88c0d0",
                "button_hover": "#5e81ac",
            },
            "Monokai": {
                "bg": "#272822",
                "fg": "#f8f8f2",
                "accent": "#66d9ef",
                "accent_dark": "#46b9cf",
                "success": "#a6e22e",
                "warning": "#e6db74",
                "danger": "#f92672",
                "sidebar": "#1e1f1c",
                "panel": "#3e3d32",
                "border": "#75715e",
                "text_bg": "#1e1f1c",
                "button": "#66d9ef",
                "button_hover": "#46b9cf",
            },
        }

        # Current theme and font settings
        self.current_theme = "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        self.editor_font_family = "Consolas"
        self.editor_font_size = 11

        # Configure dark theme
        self.setup_styles()

        # Current adventure data
        self.adventure = {
            "title": "New Adventure",
            "author": "",
            "intro": "",
            "start_room": 1,
            "rooms": [],
            "items": [],
            "monsters": [],
            "effects": [],
        }

        self.current_file = None
        self.modified = False

        self.setup_ui()
        self.new_adventure()

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")  # Use clam as base for customization

        # Configure colors
        self.root.configure(bg=self.colors["bg"])

        # Notebook (tabs)
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=self.colors["sidebar"],
            foreground=self.colors["fg"],
            padding=[20, 10],
            font=(self.current_font_family, self.current_font_size, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["accent"])],
            foreground=[("selected", "#ffffff")],
        )

        # Frames
        style.configure("TFrame", background=self.colors["bg"])
        style.configure(
            "Panel.TFrame",
            background=self.colors["panel"],
            relief="flat",
            borderwidth=1,
        )

        # Labels
        style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["fg"],
            font=(self.current_font_family, self.current_font_size),
        )
        style.configure(
            "Title.TLabel",
            font=(self.current_font_family, self.current_font_size + 4, "bold"),
            foreground=self.colors["accent"],
        )
        style.configure(
            "Subtitle.TLabel",
            font=(self.current_font_family, self.current_font_size + 1, "bold"),
            foreground=self.colors["fg"],
        )

        # Buttons
        style.configure(
            "TButton",
            background=self.colors["button"],
            foreground="#ffffff",
            borderwidth=0,
            padding=[15, 8],
            font=(self.current_font_family, self.current_font_size, "bold"),
        )
        style.map(
            "TButton",
            background=[
                ("active", self.colors["button_hover"]),
                ("pressed", self.colors["accent_dark"]),
            ],
        )

        # Success button
        style.configure(
            "Success.TButton", background=self.colors["success"], foreground="#ffffff"
        )
        style.map("Success.TButton", background=[("active", "#4cae4c")])

        # Warning button
        style.configure(
            "Warning.TButton", background=self.colors["warning"], foreground="#ffffff"
        )

        # Danger button
        style.configure(
            "Danger.TButton", background=self.colors["danger"], foreground="#ffffff"
        )

        # Entry widgets
        style.configure(
            "TEntry",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            borderwidth=1,
            relief="flat",
        )

        # Spinbox
        style.configure(
            "TSpinbox",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            arrowcolor=self.colors["fg"],
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=self.colors["text_bg"],
            foreground=self.colors["fg"],
            arrowcolor=self.colors["fg"],
        )

    def setup_ui(self):
        """Create the main UI"""
        # Menu bar with dark theme
        menubar = tk.Menu(
            self.root,
            bg=self.colors["sidebar"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(
            label="🆕 New Adventure", command=self.new_adventure, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="📂 Open...", command=self.open_adventure, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="💾 Save", command=self.save_adventure, accelerator="Ctrl+S"
        )
        file_menu.add_command(label="💾 Save As...", command=self.save_adventure_as)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.quit_ide)

        # Tools menu
        tools_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="🛠️ Tools", menu=tools_menu)
        tools_menu.add_command(
            label="▶️ Test Adventure", command=self.test_adventure, accelerator="F5"
        )
        tools_menu.add_command(
            label="✓ Validate Adventure", command=self.validate_adventure
        )
        tools_menu.add_command(label="💿 Import DSK File...", command=self.import_dsk)

        # View menu
        view_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="👁️ View", menu=view_menu)

        # Theme submenu
        theme_menu = tk.Menu(
            view_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        view_menu.add_cascade(label="🎨 Theme", menu=theme_menu)
        for theme_name in self.themes.keys():
            theme_menu.add_command(
                label=theme_name, command=lambda t=theme_name: self.change_theme(t)
            )

        # Font submenu
        font_menu = tk.Menu(
            view_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        view_menu.add_cascade(label="🔤 Font", menu=font_menu)

        # Font family submenu
        font_family_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        font_menu.add_cascade(label="Font Family", menu=font_family_menu)
        for family in [
            "Segoe UI",
            "Arial",
            "Helvetica",
            "Verdana",
            "Tahoma",
            "Calibri",
        ]:
            font_family_menu.add_command(
                label=family, command=lambda f=family: self.change_font_family(f)
            )

        # Font size submenu
        font_size_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        font_menu.add_cascade(label="Font Size", menu=font_size_menu)
        for size in [8, 9, 10, 11, 12, 14, 16]:
            font_size_menu.add_command(
                label=f"{size}pt", command=lambda s=size: self.change_font_size(s)
            )

        # Editor font submenu
        editor_font_menu = tk.Menu(
            font_menu,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        font_menu.add_cascade(label="Editor Font", menu=editor_font_menu)
        for family in [
            "Consolas",
            "Courier New",
            "Monaco",
            "Menlo",
            "Source Code Pro",
            "Fira Code",
        ]:
            editor_font_menu.add_command(
                label=family, command=lambda f=family: self.change_editor_font(f)
            )

        view_menu.add_separator()
        view_menu.add_command(
            label="↺ Reset to Defaults", command=self.reset_view_settings
        )

        # Help menu
        help_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            activebackground=self.colors["accent"],
        )
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📖 Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_adventure())
        self.root.bind("<Control-o>", lambda e: self.open_adventure())
        self.root.bind("<Control-s>", lambda e: self.save_adventure())
        self.root.bind("<F5>", lambda e: self.test_adventure())

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create tabs - Play tab first for easy access
        self.create_play_tab()
        self.create_info_tab()
        self.create_rooms_tab()
        self.create_items_tab()
        self.create_monsters_tab()
        self.create_preview_tab()

        # Status bar with color
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_bar = tk.Label(
            status_frame,
            text="✓ Ready",
            relief=tk.FLAT,
            bg=self.colors["sidebar"],
            fg=self.colors["success"],
            font=("Segoe UI", 10),
            anchor=tk.W,
            padx=10,
            pady=5,
        )
        self.status_bar.pack(fill=tk.BOTH, expand=True)

    def create_info_tab(self):
        """Adventure info tab with modern design"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="📋 Info")

        # Header
        header = ttk.Label(frame, text="Adventure Information", style="Title.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        # Create a styled container for form fields
        form_frame = ttk.Frame(frame, style="Panel.TFrame", padding="20")
        form_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Title with icon
        row = 0
        ttk.Label(form_frame, text="🎮 Adventure Title:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(
            form_frame, textvariable=self.title_var, width=60, font=("Segoe UI", 11)
        )
        title_entry.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Author
        row += 2
        ttk.Label(form_frame, text="👤 Author:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.author_var = tk.StringVar()
        author_entry = ttk.Entry(
            form_frame, textvariable=self.author_var, width=60, font=("Segoe UI", 11)
        )
        author_entry.grid(row=row + 1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Start room
        row += 2
        ttk.Label(form_frame, text="🚪 Starting Room:", style="Subtitle.TLabel").grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.start_room_var = tk.IntVar(value=1)
        room_spin = ttk.Spinbox(
            form_frame,
            from_=1,
            to=999,
            textvariable=self.start_room_var,
            width=15,
            font=("Segoe UI", 11),
        )
        room_spin.grid(row=row + 1, column=0, sticky=tk.W, pady=(0, 15))

        # Introduction
        row += 2
        ttk.Label(
            form_frame, text="📖 Introduction Text:", style="Subtitle.TLabel"
        ).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))

        # Styled text widget
        text_frame = tk.Frame(
            form_frame, bg=self.colors["text_bg"], relief=tk.FLAT, bd=1
        )
        text_frame.grid(
            row=row + 1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20)
        )
        form_frame.rowconfigure(row + 1, weight=1)

        self.intro_text = scrolledtext.ScrolledText(
            text_frame,
            width=70,
            height=12,
            wrap=tk.WORD,
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            bd=5,
        )
        self.intro_text.pack(fill=tk.BOTH, expand=True)

        # Save button - styled
        row += 2
        save_btn = ttk.Button(
            form_frame,
            text="💾 Update Adventure Info",
            command=self.update_info,
            style="Success.TButton",
        )
        save_btn.grid(row=row, column=0, sticky=tk.E, pady=(10, 0))

    def create_rooms_tab(self):
        """Rooms editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🏠 Rooms")

        # Left panel - room list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Rooms:").pack()

        self.rooms_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.rooms_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.rooms_listbox.bind("<<ListboxSelect>>", self.select_room)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.rooms_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rooms_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Room", command=self.add_room).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_room).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - room editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        # Room ID
        ttk.Label(right_panel, text="Room ID:").grid(row=0, column=0, sticky=tk.W)
        self.room_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.room_id_var).grid(
            row=0, column=1, sticky=tk.W
        )

        # Room name
        ttk.Label(right_panel, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.room_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.room_name_var, width=40).grid(
            row=1, column=1, pady=5
        )

        # Description
        ttk.Label(right_panel, text="Description:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.room_desc = scrolledtext.ScrolledText(
            right_panel, width=50, height=8, wrap=tk.WORD
        )
        self.room_desc.grid(row=3, column=0, columnspan=2, pady=5)

        # Exits
        ttk.Label(right_panel, text="Exits:").grid(row=4, column=0, sticky=tk.W, pady=5)

        exits_frame = ttk.Frame(right_panel)
        exits_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W)

        self.exit_vars = {}
        directions = [
            ("North", "north"),
            ("South", "south"),
            ("East", "east"),
            ("West", "west"),
            ("Up", "up"),
            ("Down", "down"),
        ]

        for i, (label, key) in enumerate(directions):
            row = i // 3
            col = (i % 3) * 2
            ttk.Label(exits_frame, text=f"{label}:").grid(
                row=row, column=col, sticky=tk.W, padx=5
            )
            var = tk.IntVar(value=0)
            ttk.Spinbox(exits_frame, from_=0, to=999, textvariable=var, width=8).grid(
                row=row, column=col + 1, padx=5
            )
            self.exit_vars[key] = var

        # Update button
        ttk.Button(right_panel, text="Update Room", command=self.update_room).grid(
            row=6, column=1, sticky=tk.E, pady=10
        )

    def create_items_tab(self):
        """Items editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="⚔️ Items")

        # Left panel - item list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Items:").pack()

        self.items_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.items_listbox.bind("<<ListboxSelect>>", self.select_item)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.items_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Item", command=self.add_item).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_item).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - item editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        # Item properties
        row = 0
        ttk.Label(right_panel, text="Item ID:").grid(row=row, column=0, sticky=tk.W)
        self.item_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.item_id_var).grid(
            row=row, column=1, sticky=tk.W
        )

        row += 1
        ttk.Label(right_panel, text="Name:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.item_name_var, width=40).grid(
            row=row, column=1, pady=3
        )

        row += 1
        ttk.Label(right_panel, text="Description:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_desc = scrolledtext.ScrolledText(
            right_panel, width=40, height=4, wrap=tk.WORD
        )
        self.item_desc.grid(row=row + 1, column=0, columnspan=2, pady=3)

        row += 2
        ttk.Label(right_panel, text="Weight:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_weight_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=0, to=1000, textvariable=self.item_weight_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Value:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_value_var = tk.IntVar(value=0)
        ttk.Spinbox(
            right_panel, from_=0, to=10000, textvariable=self.item_value_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Location (Room):").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.item_location_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=0, to=999, textvariable=self.item_location_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        self.item_is_weapon_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right_panel, text="Is Weapon", variable=self.item_is_weapon_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=3)

        row += 1
        self.item_is_takeable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            right_panel, text="Can Be Taken", variable=self.item_is_takeable_var
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=3)

        row += 1
        ttk.Button(right_panel, text="Update Item", command=self.update_item).grid(
            row=row, column=1, sticky=tk.E, pady=10
        )

    def create_monsters_tab(self):
        """Monsters editor tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="👾 Monsters")

        # Left panel - monster list
        left_panel = ttk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=5)

        ttk.Label(left_panel, text="Monsters/NPCs:").pack()

        self.monsters_listbox = tk.Listbox(left_panel, width=30, height=25)
        self.monsters_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.monsters_listbox.bind("<<ListboxSelect>>", self.select_monster)

        scrollbar = ttk.Scrollbar(
            left_panel, orient=tk.VERTICAL, command=self.monsters_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.monsters_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add Monster", command=self.add_monster).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Delete", command=self.delete_monster).pack(
            side=tk.LEFT, padx=2
        )

        # Right panel - monster editor
        right_panel = ttk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)
        frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(right_panel, text="Monster ID:").grid(row=row, column=0, sticky=tk.W)
        self.monster_id_var = tk.IntVar()
        ttk.Label(right_panel, textvariable=self.monster_id_var).grid(
            row=row, column=1, sticky=tk.W
        )

        row += 1
        ttk.Label(right_panel, text="Name:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_name_var = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.monster_name_var, width=40).grid(
            row=row, column=1, pady=3
        )

        row += 1
        ttk.Label(right_panel, text="Description:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_desc = scrolledtext.ScrolledText(
            right_panel, width=40, height=4, wrap=tk.WORD
        )
        self.monster_desc.grid(row=row + 1, column=0, columnspan=2, pady=3)

        row += 2
        ttk.Label(right_panel, text="Room:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_room_var = tk.IntVar(value=1)
        ttk.Spinbox(
            right_panel, from_=1, to=999, textvariable=self.monster_room_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Hardiness (HP):").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_hardiness_var = tk.IntVar(value=10)
        ttk.Spinbox(
            right_panel,
            from_=1,
            to=100,
            textvariable=self.monster_hardiness_var,
            width=10,
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Agility:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_agility_var = tk.IntVar(value=10)
        ttk.Spinbox(
            right_panel, from_=1, to=30, textvariable=self.monster_agility_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Friendliness:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_friendliness_var = tk.StringVar(value="hostile")
        ttk.Combobox(
            right_panel,
            textvariable=self.monster_friendliness_var,
            values=["friendly", "neutral", "hostile"],
            width=15,
            state="readonly",
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Label(right_panel, text="Gold:").grid(
            row=row, column=0, sticky=tk.W, pady=3
        )
        self.monster_gold_var = tk.IntVar(value=0)
        ttk.Spinbox(
            right_panel, from_=0, to=1000, textvariable=self.monster_gold_var, width=10
        ).grid(row=row, column=1, sticky=tk.W, pady=3)

        row += 1
        ttk.Button(
            right_panel, text="Update Monster", command=self.update_monster
        ).grid(row=row, column=1, sticky=tk.E, pady=10)

    def create_preview_tab(self):
        """JSON preview tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📄 JSON")

        ttk.Label(frame, text="Adventure JSON:").pack(anchor=tk.W)

        self.preview_text = scrolledtext.ScrolledText(
            frame, width=80, height=35, wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh Preview", command=self.update_preview).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_preview).pack(
            side=tk.LEFT, padx=5
        )

    def create_play_tab(self):
        """Interactive play tab with modern design"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="▶️ Play")

        # Header
        header = ttk.Label(frame, text="Adventure Playthrough", style="Title.TLabel")
        header.pack(anchor=tk.W, pady=(0, 15))

        # Game output area with modern styling
        output_frame = tk.Frame(frame, bg=self.colors["text_bg"], relief=tk.FLAT, bd=2)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.game_output = scrolledtext.ScrolledText(
            output_frame,
            width=90,
            height=28,
            wrap=tk.WORD,
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Consolas", 10),
            insertbackground="#58a6ff",
            relief=tk.FLAT,
            bd=10,
        )
        self.game_output.pack(fill=tk.BOTH, expand=True)
        self.game_output.config(state=tk.DISABLED)

        # Configure text tags for colored output
        self.game_output.tag_config("success", foreground="#3fb950")
        self.game_output.tag_config("warning", foreground="#d29922")
        self.game_output.tag_config("error", foreground="#f85149")
        self.game_output.tag_config("info", foreground="#58a6ff")

        # Command input area with modern styling
        cmd_container = tk.Frame(frame, bg=self.colors["panel"], relief=tk.FLAT, bd=1)
        cmd_container.pack(fill=tk.X, pady=(0, 15))

        cmd_frame = tk.Frame(cmd_container, bg=self.colors["panel"])
        cmd_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(cmd_frame, text="💬", font=("Segoe UI", 14)).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        self.command_entry = tk.Entry(
            cmd_frame,
            font=("Consolas", 11),
            bg=self.colors["text_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["accent"],
            relief=tk.FLAT,
            bd=5,
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind("<Return>", lambda e: self.send_command())

        send_btn = ttk.Button(
            cmd_frame, text="➤ Send", command=self.send_command, style="Success.TButton"
        )
        send_btn.pack(side=tk.LEFT)

        # Control buttons with colors
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X)

        ttk.Button(
            control_frame,
            text="📂 Load Adventure",
            command=self.load_for_play,
            width=18,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="▶️ Start Game",
            command=self.start_game,
            width=15,
            style="Success.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="⟳ Restart",
            command=self.restart_game,
            width=15,
            style="Warning.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame,
            text="🗑️ Clear Output",
            command=self.clear_game_output,
            width=15,
        ).pack(side=tk.LEFT, padx=5)

        # Initialize game state
        self.game_instance = None
        self.game_running = False

    # Adventure management methods
    def new_adventure(self):
        """Create a new adventure"""
        if self.modified and not messagebox.askyesno(
            "Unsaved Changes", "You have unsaved changes. Continue anyway?"
        ):
            return

        self.adventure = {
            "title": "New Adventure",
            "author": "",
            "intro": "",
            "start_room": 1,
            "rooms": [],
            "items": [],
            "monsters": [],
            "effects": [],
        }

        self.current_file = None
        self.modified = False
        self.load_adventure_to_ui()
        self.update_status("New adventure created")

    def open_adventure(self):
        """Open an existing adventure"""
        filename = filedialog.askopenfilename(
            title="Open Adventure",
            initialdir="adventures",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            with open(filename, "r") as f:
                self.adventure = json.load(f)

            self.current_file = filename
            self.modified = False
            self.load_adventure_to_ui()
            self.update_status(f"Opened: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_adventure(self):
        """Save the current adventure"""
        if not self.current_file:
            return self.save_adventure_as()

        try:
            self.collect_adventure_data()
            with open(self.current_file, "w") as f:
                json.dump(self.adventure, f, indent=2)

            self.modified = False
            self.update_status(f"Saved: {os.path.basename(self.current_file)}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")
            return False

    def save_adventure_as(self):
        """Save adventure with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Save Adventure As",
            initialdir="adventures",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return False

        self.current_file = filename
        return self.save_adventure()

    def load_adventure_to_ui(self):
        """Load adventure data into UI"""
        # Info tab
        self.title_var.set(self.adventure.get("title", ""))
        self.author_var.set(self.adventure.get("author", ""))
        self.start_room_var.set(self.adventure.get("start_room", 1))
        self.intro_text.delete("1.0", tk.END)
        self.intro_text.insert("1.0", self.adventure.get("intro", ""))

        # Rooms
        self.refresh_rooms_list()

        # Items
        self.refresh_items_list()

        # Monsters
        self.refresh_monsters_list()

        # Preview
        self.update_preview()

    def collect_adventure_data(self):
        """Collect data from UI into adventure dict"""
        self.adventure["title"] = self.title_var.get()
        self.adventure["author"] = self.author_var.get()
        self.adventure["start_room"] = self.start_room_var.get()
        self.adventure["intro"] = self.intro_text.get("1.0", tk.END).strip()

    # Room methods
    def refresh_rooms_list(self):
        """Refresh the rooms listbox"""
        self.rooms_listbox.delete(0, tk.END)
        for room in self.adventure["rooms"]:
            self.rooms_listbox.insert(tk.END, f"#{room['id']}: {room['name']}")

    def add_room(self):
        """Add a new room"""
        new_id = max([r["id"] for r in self.adventure["rooms"]], default=0) + 1
        room = {
            "id": new_id,
            "name": f"Room {new_id}",
            "description": "A new room.",
            "exits": {},
            "is_dark": False,
        }
        self.adventure["rooms"].append(room)
        self.refresh_rooms_list()
        self.rooms_listbox.selection_set(tk.END)
        self.select_room(None)
        self.modified = True

    def delete_room(self):
        """Delete selected room"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this room?"):
            idx = selection[0]
            del self.adventure["rooms"][idx]
            self.refresh_rooms_list()
            self.modified = True

    def select_room(self, event):
        """Load selected room into editor"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        room = self.adventure["rooms"][selection[0]]
        self.room_id_var.set(room["id"])
        self.room_name_var.set(room["name"])
        self.room_desc.delete("1.0", tk.END)
        self.room_desc.insert("1.0", room["description"])

        for direction, var in self.exit_vars.items():
            var.set(room["exits"].get(direction, 0))

    def update_room(self):
        """Update current room from editor"""
        selection = self.rooms_listbox.curselection()
        if not selection:
            return

        room = self.adventure["rooms"][selection[0]]
        room["name"] = self.room_name_var.get()
        room["description"] = self.room_desc.get("1.0", tk.END).strip()

        room["exits"] = {}
        for direction, var in self.exit_vars.items():
            if var.get() > 0:
                room["exits"][direction] = var.get()

        self.refresh_rooms_list()
        self.rooms_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Room updated")

    def update_info(self):
        """Update adventure info"""
        self.collect_adventure_data()
        self.modified = True
        self.update_status("Adventure info updated")

    # Item methods
    def refresh_items_list(self):
        """Refresh items listbox"""
        self.items_listbox.delete(0, tk.END)
        for item in self.adventure["items"]:
            self.items_listbox.insert(tk.END, f"#{item['id']}: {item['name']}")

    def add_item(self):
        """Add a new item"""
        new_id = max([i["id"] for i in self.adventure["items"]], default=0) + 1
        item = {
            "id": new_id,
            "name": f"Item {new_id}",
            "description": "A new item.",
            "type": "normal",
            "weight": 1,
            "value": 0,
            "is_weapon": False,
            "is_takeable": True,
            "location": 1,
        }
        self.adventure["items"].append(item)
        self.refresh_items_list()
        self.items_listbox.selection_set(tk.END)
        self.select_item(None)
        self.modified = True

    def delete_item(self):
        """Delete selected item"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this item?"):
            idx = selection[0]
            del self.adventure["items"][idx]
            self.refresh_items_list()
            self.modified = True

    def select_item(self, event):
        """Load selected item into editor"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        item = self.adventure["items"][selection[0]]
        self.item_id_var.set(item["id"])
        self.item_name_var.set(item["name"])
        self.item_desc.delete("1.0", tk.END)
        self.item_desc.insert("1.0", item["description"])
        self.item_weight_var.set(item.get("weight", 1))
        self.item_value_var.set(item.get("value", 0))
        self.item_location_var.set(item.get("location", 1))
        self.item_is_weapon_var.set(item.get("is_weapon", False))
        self.item_is_takeable_var.set(item.get("is_takeable", True))

    def update_item(self):
        """Update current item"""
        selection = self.items_listbox.curselection()
        if not selection:
            return

        item = self.adventure["items"][selection[0]]
        item["name"] = self.item_name_var.get()
        item["description"] = self.item_desc.get("1.0", tk.END).strip()
        item["weight"] = self.item_weight_var.get()
        item["value"] = self.item_value_var.get()
        item["location"] = self.item_location_var.get()
        item["is_weapon"] = self.item_is_weapon_var.get()
        item["is_takeable"] = self.item_is_takeable_var.get()

        self.refresh_items_list()
        self.items_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Item updated")

    # Monster methods
    def refresh_monsters_list(self):
        """Refresh monsters listbox"""
        self.monsters_listbox.delete(0, tk.END)
        for monster in self.adventure["monsters"]:
            self.monsters_listbox.insert(tk.END, f"#{monster['id']}: {monster['name']}")

    def add_monster(self):
        """Add a new monster"""
        new_id = max([m["id"] for m in self.adventure["monsters"]], default=0) + 1
        monster = {
            "id": new_id,
            "name": f"Monster {new_id}",
            "description": "A new creature.",
            "room_id": 1,
            "hardiness": 10,
            "agility": 10,
            "friendliness": "hostile",
            "courage": 100,
            "gold": 0,
        }
        self.adventure["monsters"].append(monster)
        self.refresh_monsters_list()
        self.monsters_listbox.selection_set(tk.END)
        self.select_monster(None)
        self.modified = True

    def delete_monster(self):
        """Delete selected monster"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        if messagebox.askyesno("Confirm", "Delete this monster?"):
            idx = selection[0]
            del self.adventure["monsters"][idx]
            self.refresh_monsters_list()
            self.modified = True

    def select_monster(self, event):
        """Load selected monster into editor"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        monster = self.adventure["monsters"][selection[0]]
        self.monster_id_var.set(monster["id"])
        self.monster_name_var.set(monster["name"])
        self.monster_desc.delete("1.0", tk.END)
        self.monster_desc.insert("1.0", monster["description"])
        self.monster_room_var.set(monster.get("room_id", 1))
        self.monster_hardiness_var.set(monster.get("hardiness", 10))
        self.monster_agility_var.set(monster.get("agility", 10))
        self.monster_friendliness_var.set(monster.get("friendliness", "hostile"))
        self.monster_gold_var.set(monster.get("gold", 0))

    def update_monster(self):
        """Update current monster"""
        selection = self.monsters_listbox.curselection()
        if not selection:
            return

        monster = self.adventure["monsters"][selection[0]]
        monster["name"] = self.monster_name_var.get()
        monster["description"] = self.monster_desc.get("1.0", tk.END).strip()
        monster["room_id"] = self.monster_room_var.get()
        monster["hardiness"] = self.monster_hardiness_var.get()
        monster["agility"] = self.monster_agility_var.get()
        monster["friendliness"] = self.monster_friendliness_var.get()
        monster["gold"] = self.monster_gold_var.get()

        self.refresh_monsters_list()
        self.monsters_listbox.selection_set(selection[0])
        self.modified = True
        self.update_status("Monster updated")

    # Preview methods
    def update_preview(self):
        """Update JSON preview"""
        self.collect_adventure_data()
        json_text = json.dumps(self.adventure, indent=2)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", json_text)

    def copy_preview(self):
        """Copy preview to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.preview_text.get("1.0", tk.END))
        self.update_status("JSON copied to clipboard")

    # Tool methods
    def test_adventure(self):
        """Test the adventure in the game"""
        # Save to temp file
        temp_file = "adventures/_temp_test.json"
        self.collect_adventure_data()

        try:
            with open(temp_file, "w") as f:
                json.dump(self.adventure, f, indent=2)

            # Launch game
            subprocess.Popen(["./play_adventure.sh", "_temp_test.json"])
            self.update_status("Testing adventure...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test:\n{e}")

    def validate_adventure(self):
        """Validate adventure data"""
        self.collect_adventure_data()
        errors = []

        if not self.adventure["title"]:
            errors.append("Adventure must have a title")

        if not self.adventure["rooms"]:
            errors.append("Adventure must have at least one room")

        # Check start room exists
        start_room = self.adventure["start_room"]
        if not any(r["id"] == start_room for r in self.adventure["rooms"]):
            errors.append(f"Start room {start_room} does not exist")

        # Check room exits
        room_ids = {r["id"] for r in self.adventure["rooms"]}
        for room in self.adventure["rooms"]:
            for direction, target in room["exits"].items():
                if target not in room_ids and target != 0:
                    errors.append(
                        f"Room {room['id']} has exit to non-existent " f"room {target}"
                    )

        if errors:
            messagebox.showwarning("Validation Issues", "\n".join(errors))
        else:
            messagebox.showinfo("Validation", "Adventure is valid!")

    def import_dsk(self):
        """Import a DSK file"""
        filename = filedialog.askopenfilename(
            title="Import DSK File",
            filetypes=[("DSK files", "*.dsk"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            # Run converter
            result = subprocess.run(
                ["python3", "dsk_converter.py", filename, "adventures/_imported.json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Load the imported adventure
                with open("adventures/_imported.json", "r") as f:
                    self.adventure = json.load(f)

                self.current_file = None
                self.modified = True
                self.load_adventure_to_ui()
                self.update_status("DSK file imported successfully")
            else:
                messagebox.showerror("Import Failed", result.stderr or "Unknown error")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import:\n{e}")

    def show_help(self):
        """Show help dialog"""
        help_text = """Adventure Construction Set - Quick Start

Creating Adventures:
1. Fill in Adventure Info (title, author, intro)
2. Add Rooms (locations in your adventure)
3. Add Items (treasures, weapons, objects)
4. Add Monsters (enemies and NPCs)
5. Test your adventure (F5)
6. Save when done (Ctrl+S)

Tips:
- Room 0 exits = no exit
- Set start room to first room ID
- Use Preview tab to see JSON
- Test frequently while building
- Use Validate to check for errors
- Compatible with classic Eamon format & Apple II DSK files

Keyboard Shortcuts:
Ctrl+N - New Adventure
Ctrl+O - Open Adventure
Ctrl+S - Save Adventure
F5 - Test Adventure
"""
        messagebox.showinfo("Quick Start Guide", help_text)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "🎮 Adventure Construction Set v2.0\n\n"
            "A complete IDE for creating text adventures\n"
            "Compatible with classic Eamon format\n\n"
            "Features:\n"
            "• Visual room editor\n"
            "• Item and NPC management\n"
            "• Adventure testing\n"
            "• DSK file import\n"
            "• 5 beautiful themes (Dark, Light, Dracula, Nord, Monokai)\n"
            "• Customizable fonts\n"
            "• 30 natural language commands\n\n"
            "Version 2.0 - Enhanced Edition",
        )

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)

    # Game play methods
    def print_game(self, text):
        """Print text to game output"""
        self.game_output.config(state=tk.NORMAL)
        self.game_output.insert(tk.END, text + "\n")
        self.game_output.see(tk.END)
        self.game_output.config(state=tk.DISABLED)

    def clear_game_output(self):
        """Clear the game output"""
        self.game_output.config(state=tk.NORMAL)
        self.game_output.delete("1.0", tk.END)
        self.game_output.config(state=tk.DISABLED)

    def load_for_play(self):
        """Load an adventure file to play"""
        filename = filedialog.askopenfilename(
            title="Load Adventure to Play",
            initialdir="adventures",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            with open(filename, "r") as f:
                self.adventure = json.load(f)

            self.current_file = filename
            self.modified = False
            self.load_adventure_to_ui()

            # Show message in game output
            self.clear_game_output()
            self.print_game("=" * 60)
            self.print_game(f"  LOADED: {self.adventure.get('title', 'Untitled')}")
            self.print_game("=" * 60)
            self.print_game("")
            self.print_game("Click '▶ Start Game' to begin playing!")
            self.print_game("")

            self.update_status(f"Loaded: {os.path.basename(filename)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load:\n{e}")

    def start_game(self):
        """Start playing the loaded adventure"""
        # Save current adventure to temp file
        temp_file = "adventures/_temp_play.json"
        self.collect_adventure_data()

        try:
            with open(temp_file, "w") as f:
                json.dump(self.adventure, f, indent=2)

            # Import and start game engine
            import importlib.util

            engine_path = (
                Path(__file__).parent.parent.parent.parent / "acs_engine_enhanced.py"
            )
            spec = importlib.util.spec_from_file_location(
                "acs_engine_enhanced", engine_path
            )
            acs_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(acs_module)

            self.clear_game_output()
            self.game_instance = acs_module.EnhancedEamonGame(temp_file)
            self.game_instance.load_adventure()
            self.game_running = True

            # Print introduction
            self.print_game("=" * 60)
            title = self.game_instance.adventure_title.upper()
            self.print_game(f"  {title}")
            self.print_game("=" * 60)
            self.print_game("")
            self.print_game(self.game_instance.adventure_intro)
            self.print_game("")
            self.print_game("=" * 60)
            self.print_game("")

            # Show starting room - capture output
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            self.game_instance.look()

            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            if output:
                self.print_game(output.rstrip())

            self.command_entry.focus()
            self.update_status("Game started - enter commands below")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game:\n{e}")
            self.game_running = False

    def restart_game(self):
        """Restart the current game"""
        if self.game_running:
            self.start_game()
        else:
            messagebox.showinfo("No Game", "Please start a game first")

    def send_command(self):
        """Send command to game engine"""
        if not self.game_running:
            messagebox.showinfo(
                "No Game", "Please start the game first using '▶ Start Game'"
            )
            return

        command = self.command_entry.get().strip()
        if not command:
            return

        # Display the command
        self.print_game(f"\n> {command}")
        self.command_entry.delete(0, tk.END)

        # Handle special commands
        if command.lower() in ["quit", "q", "exit"]:
            self.print_game("\nThanks for playing!")
            self.print_game("=" * 60)
            self.game_running = False
            self.update_status("Game ended")
            return

        # Process command through game engine
        try:
            # Capture the game's output
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            # Process the command
            self.game_instance.process_command(command)

            # Get the output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            # Display output
            if output:
                self.print_game(output.rstrip())

            # Check if game is over
            if (
                hasattr(self.game_instance, "game_over")
                and self.game_instance.game_over
            ):
                self.print_game("\n" + "=" * 60)
                self.print_game("GAME OVER")
                self.print_game("=" * 60)
                self.game_running = False
                self.update_status("Game ended")

        except Exception as e:
            sys.stdout = old_stdout
            self.print_game(f"\nError: {e}")

    def change_theme(self, theme_name):
        """Change the color theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.colors = self.themes[theme_name]
            self.setup_styles()
            self.refresh_all_widgets()
            self.update_status(f"Theme changed to: {theme_name}")

    def change_font_family(self, font_family):
        """Change the UI font family"""
        self.current_font_family = font_family
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font changed to: {font_family}")

    def change_font_size(self, font_size):
        """Change the UI font size"""
        self.current_font_size = font_size
        self.setup_styles()
        self.refresh_all_widgets()
        self.update_status(f"Font size changed to: {font_size}pt")

    def change_editor_font(self, font_family):
        """Change the editor font family"""
        self.editor_font_family = font_family
        self.apply_editor_fonts()
        self.update_status(f"Editor font changed to: {font_family}")

    def apply_editor_fonts(self):
        """Apply editor font to all text widgets"""
        editor_font = (self.editor_font_family, self.editor_font_size)

        # Update intro text
        if hasattr(self, "intro_text"):
            self.intro_text.config(font=editor_font)

        # Update description text
        if hasattr(self, "description_text"):
            self.description_text.config(font=editor_font)

        # Update game output
        if hasattr(self, "game_output"):
            self.game_output.config(font=editor_font)

    def refresh_all_widgets(self):
        """Refresh all widgets to apply new theme"""
        # Re-setup the UI with new colors
        self.root.configure(bg=self.colors["bg"])

        # Update status bar
        if hasattr(self, "status_bar"):
            self.status_bar.config(bg=self.colors["panel"], fg=self.colors["fg"])

        # Update all text widgets with new colors
        if hasattr(self, "intro_text"):
            self.intro_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if hasattr(self, "description_text"):
            self.description_text.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

        if hasattr(self, "game_output"):
            self.game_output.config(bg=self.colors["text_bg"], fg=self.colors["fg"])

        if hasattr(self, "game_input"):
            self.game_input.config(
                bg=self.colors["text_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
            )

    def reset_view_settings(self):
        """Reset theme and font to defaults"""
        self.current_theme = "Dark"
        self.colors = self.themes[self.current_theme]
        self.current_font_family = "Segoe UI"
        self.current_font_size = 10
        self.editor_font_family = "Consolas"
        self.editor_font_size = 11
        self.setup_styles()
        self.refresh_all_widgets()
        self.apply_editor_fonts()
        self.update_status("View settings reset to defaults")

    def quit_ide(self):
        """Quit the IDE"""
        if self.modified and not messagebox.askyesno(
            "Unsaved Changes", "You have unsaved changes. Quit anyway?"
        ):
            return

        self.root.quit()


def main():
    """Main entry point"""
    root = tk.Tk()
    AdventureIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
