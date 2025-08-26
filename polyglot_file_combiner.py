# --------------------------------##-----imports --------#
import io
import os
import sys
import time
import json
import shutil
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional, Tuple

# Optional previews (graceful fallback)
try:
    from PIL import Image, ImageTk

    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import PyPDF2

    PDF_OK = True
except ImportError:
    PDF_OK = False


# --------------------------------##-----Constants and Configuration --------#
class AppConfig:
    """Centralized configuration for the application."""
    APP_NAME = "Polyglot File Combiner"
    APP_VER = "1.0"  # Update as needed
    CONFIG_PATH = Path.home() / "polyglot_combiner.json"

    SUPPORTED_TYPES = {
        "PDF": [".pdf"], "ZIP": [".zip"], "JPEG": [".jpg", ".jpeg"],
        "PNG": [".png"], "GIF": [".gif"], "MP3": [".mp3"],
        "MP4": [".mp4"], "TXT": [".txt", ".csv", ".log", ".md", ".html", ".htm"],
        "SCRIPT": [".bat", ".cmd", ".ps1", ".sh", ".bash", ".py"],
    }
    FILE_FILTERS_ALL = [
        ("All supported",
         "*.pdf *.zip *.jpg *.jpeg *.png *.gif *.mp3 *.mp4 *.txt *.csv *.log *.md *.html *.htm *.bat *.cmd *.ps1 *.sh *.bash *.py"),
        ("PDF", "*.pdf"), ("ZIP", "*.zip"), ("Images", "*.jpg *.jpeg *.png *.gif"),
        ("Text", "*.txt *.csv *.log *.md *.html *.htm"), ("Scripts", "*.bat *.cmd *.ps1 *.sh *.bash *.py"),
        ("Audio", "*.mp3"), ("Video", "*.mp4"), ("All files", "*.*"),
    ]
    SCRIPT_TEMPLATES = {
        "Batch (.bat)": r"""@echo off
rem --- Self-extract notice ---
echo %~nx0 has a ZIP payload at the end. Open with an unzip tool to extract.
exit /b 0
""", "PowerShell (.ps1)": r"""# Self-extract notice
Write-Host "$($MyInvocation.MyCommand.Name) has a ZIP payload at the end. Open with an unzip tool."
exit 0
""", "POSIX sh (.sh)": r"""#!/bin/sh
echo "$(basename "$0") has a ZIP payload at the end. Open with an unzip tool."
exit 0
""", "Bash (.bash)": r"""#!/usr/bin/env bash
echo "$(basename "$0") has a ZIP payload at the end. Open with an unzip tool."
exit 0
""", "Python (.py)": r"""# Self-extract notice
print(f"{__file__} has a ZIP payload at the end. Open with an unzip tool.")
"""
    }
    COMBINATIONS = [
        {"label": "TXT + Images", "primary": "TXT", "secondaries": ["JPEG", "PNG", "GIF"], "strategy": "ZIP-last"},
        {"label": "PDF + Images", "primary": "PDF", "secondaries": ["JPEG", "PNG", "GIF"], "strategy": "ZIP-last"},
        {"label": "JPEG + Extras", "primary": "JPEG", "secondaries": ["TXT", "PNG", "GIF", "MP3", "MP4"],
         "strategy": "ZIP-last"},
        {"label": "PNG + Extras", "primary": "PNG", "secondaries": ["TXT", "JPEG", "GIF", "MP3", "MP4"],
         "strategy": "ZIP-last"},
        {"label": "GIF + Extras", "primary": "GIF", "secondaries": ["TXT", "JPEG", "PNG", "MP3", "MP4"],
         "strategy": "ZIP-last"},
        {"label": "MP3 + Text", "primary": "MP3", "secondaries": ["TXT"], "strategy": "ZIP-last"},
        {"label": "MP4 + Text", "primary": "MP4", "secondaries": ["TXT"], "strategy": "ZIP-last"},
        {"label": "Batch (.bat) + Payload", "primary": "SCRIPT",
         "secondaries": ["TXT", "JPEG", "PNG", "GIF", "MP3", "MP4"], "strategy": "Script+ZIP"},
        {"label": "PowerShell (.ps1) + Payload", "primary": "SCRIPT", "secondaries": ["TXT", "JPEG", "PNG", "GIF"],
         "strategy": "Script+ZIP"},
        {"label": "Shell (.sh/.bash) + Payload", "primary": "SCRIPT", "secondaries": ["TXT", "JPEG", "PNG"],
         "strategy": "Script+ZIP"},
        {"label": "Python (.py) + Payload", "primary": "SCRIPT", "secondaries": ["TXT", "PNG", "GIF"],
         "strategy": "Script+ZIP"},
        {"label": "ZIP only (container)", "primary": "ZIP", "secondaries": [], "strategy": "ZIP-last"},
    ]


class Theme:
    """Manages color palettes and applies them to widgets by creating custom styles."""
    LIGHT = {
        "bg": "#fdfdfd", "fg": "#1f1f1f", "btn_fg": "#1f1f1f", "panel": "#f2f2f2",
        "accent": "#002D62", "text_bg": "#ffffff", "text_fg": "#111111", "canvas_bg": "#f0f0f0",
        "btn_bg": "#f0f0f0", "btn_active_bg": "#e5e5e5", "lbl_frame_border": "#d0d0d0",
        "menu_bg": "#fdfdfd", "menu_fg": "#1f1f1f", "menu_active_bg": "#002D62", "menu_active_fg": "#ffffff"
    }
    DARK = {
        "bg": "#1e1f22", "fg": "#e6e6e6", "btn_fg": "#e6e6e6", "panel": "#2b2d31",
        "accent": "#002D62", "text_bg": "#1f2125", "text_fg": "#eaeaea", "canvas_bg": "#2a2c30",
        "btn_bg": "#2b2d31", "btn_active_bg": "#3c3f41", "lbl_frame_border": "#3c3f41",
        "menu_bg": "#2b2d31", "menu_fg": "#e6e6e6", "menu_active_bg": "#002D62", "menu_active_fg": "#ffffff"
    }
    # --- NEW "PythonPlus" THEME PALETTE ---
    BLUE_YELLOW = {
        "bg": "#20304A",  # Dark navy blue background
        "fg": "#D0D0D0",  # Light grey text for labels
        "btn_fg": "#FFFF80",  # Bright yellow text for buttons
        "panel": "#30405A",  # Slightly lighter blue for panels/headers
        "accent": "#FFFF80",  # The same yellow for accents/highlights
        "text_bg": "#FFFFFF",  # White background for input fields
        "text_fg": "#000000",  # Black text inside input fields
        "canvas_bg": "#30405A",  # Panel color for canvas background
        "btn_bg": "#40729F",  # Medium blue for buttons
        "btn_active_bg": "#5082AF",  # Lighter blue for button hover
        "lbl_frame_border": "#40506A",  # Border color for frames
        "menu_bg": "#20304A",  # Menu background
        "menu_fg": "#D0D0D0",  # Menu text
        "menu_active_bg": "#40729F",  # Menu hover background
        "menu_active_fg": "#FFFF80"  # Menu hover text
    }

    BUTTON_STYLE = "App.TButton"
    LABELFRAME_STYLE = "App.TLabelframe"

    @staticmethod
    def get_palette(theme_name: str) -> dict:
        if theme_name == "dark": return Theme.DARK
        if theme_name == "blue_yellow": return Theme.BLUE_YELLOW
        return Theme.LIGHT

    @staticmethod
    def apply(root: tk.Tk, style: ttk.Style, palette: dict, menubar: tk.Menu):
        root.configure(bg=palette["bg"])
        style.theme_use('clam')

        # General widgets
        style.configure(".", background=palette["bg"], foreground=palette["fg"], fieldbackground=palette["text_bg"])
        style.configure("TFrame", background=palette["bg"])
        style.configure("TLabel", background=palette["bg"], foreground=palette["fg"])
        style.configure("TSeparator", background=palette["panel"])
        style.configure("TPanedwindow", background=palette["bg"])
        style.configure("Sash", sashrelief="flat", sashthickness=6, background=palette["panel"])

        # Entry and Combobox
        style.configure("TEntry", fieldbackground=palette["text_bg"], foreground=palette["text_fg"],
                        bordercolor=palette["panel"], insertcolor=palette["text_fg"])
        style.map("TCombobox", fieldbackground=[('readonly', palette["text_bg"])])
        style.configure("TCombobox", foreground=palette["text_fg"], bordercolor=palette["panel"])

        # Labelframe
        style.configure(Theme.LABELFRAME_STYLE, background=palette["bg"], bordercolor=palette["lbl_frame_border"],
                        relief="solid", borderwidth=1)
        style.configure(f"{Theme.LABELFRAME_STYLE}.Label", background=palette["bg"], foreground=palette["fg"])

        # --- CRUCIAL BUTTON STYLE UPDATE ---
        style.layout(Theme.BUTTON_STYLE, [('Button.border', {'sticky': 'nswe', 'children': [
            ('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})])
        style.configure(
            Theme.BUTTON_STYLE,
            foreground=palette["btn_fg"],  # Use the specific button foreground color
            background=palette["btn_bg"],
            padding=(8, 6),
            relief="raised",
            bordercolor=palette["panel"],
            borderwidth=1,
            font=("Segoe UI", 9, "bold")
        )
        style.map(Theme.BUTTON_STYLE, background=[('active', palette["btn_active_bg"]), ('pressed', palette["accent"])],
                  relief=[('pressed', 'sunken')])

        # Treeview
        style.configure("Treeview", background=palette["text_bg"], fieldbackground=palette["text_bg"],
                        foreground=palette["text_fg"], rowheight=25)
        selected_fg = "#000000" if palette == Theme.BLUE_YELLOW else "#ffffff"
        style.map("Treeview", background=[('selected', palette["accent"])], foreground=[('selected', selected_fg)])
        style.configure("Treeview.Heading", background=palette["panel"], foreground=palette["fg"], relief="flat",
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview.Heading", background=[('active', palette["btn_active_bg"])])

        # Menubar
        menubar.config(bg=palette["menu_bg"], fg=palette["menu_fg"], activebackground=palette["menu_active_bg"],
                       activeforeground=palette["menu_active_fg"], relief='flat')
        for menu in menubar.winfo_children():
            menu.config(bg=palette["menu_bg"], fg=palette["menu_fg"], activebackground=palette["menu_active_bg"],
                        activeforeground=palette["menu_active_fg"], relief='flat')

    @staticmethod
    def apply_to_widget(widget: tk.Widget, theme_name: str, widget_type: str):
        palette = Theme.get_palette(theme_name)
        config = {}
        if widget_type == "text":
            config = {"bg": palette["text_bg"], "fg": palette["text_fg"], "insertbackground": palette["text_fg"],
                      "relief": "solid", "borderwidth": 1, "highlightthickness": 0}
        elif widget_type == "canvas":
            config = {"bg": palette["canvas_bg"], "highlightthickness": 0}
        elif widget_type == "listbox":
            config = {"bg": palette["text_bg"], "fg": palette["text_fg"], "selectbackground": palette["accent"],
                      "selectforeground": "#000000", "highlightthickness": 0}
        if config: widget.configure(**config)


# --------------------------------##-----helpers --------#
def human_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"];
    f = float(n)
    for u in units:
        if f < 1024.0 or u == units[-1]: return f"{f:.0f} {u}" if u == "B" else f"{f:.1f} {u}"
        f /= 1024.0
    return f"{f:.1f} {units[-1]}"


def detect_type(p: Path) -> str:
    ext = p.suffix.lower()
    for t, exts in AppConfig.SUPPORTED_TYPES.items():
        if ext in exts: return t
    return "UNKNOWN"


def filters_for(type_name: str) -> List[Tuple[str, str]]:
    exts = AppConfig.SUPPORTED_TYPES.get(type_name)
    if not exts: return AppConfig.FILE_FILTERS_ALL
    pat = " ".join(f"*{e}" for e in exts)
    return [(f"{type_name}", pat), ("All files", "*.*")]


# --------------------------------##-----File Operation Logic --------#
class FileCombiner:
    @staticmethod
    def create_zip_payload(pairs: List[Tuple[str, Path]]) -> bytes:
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for arcname, p in pairs: zf.write(p, arcname)
        return bio.getvalue()

    @staticmethod
    def write_zip_last(primary_path: Path, zip_payload: bytes, output_path: Path):
        with primary_path.open("rb") as src, output_path.open("wb") as out:
            shutil.copyfileobj(src, out)
            out.write(zip_payload)

    @staticmethod
    def write_script_zip(stub_text: str, zip_payload: bytes, output_path: Path, encoding="utf-8"):
        with output_path.open("wb") as out:
            out.write(stub_text.encode(encoding, errors="replace"))
            if not stub_text.endswith("\n"): out.write(b"\n")
            out.write(zip_payload)


# --------------------------------##-----Preview Logic --------#
class PreviewGenerator:
    MAX_TEXT_CHARS = 4000

    @staticmethod
    def get_text_preview(p: Path) -> str:
        file_type = detect_type(p)
        try:
            if file_type in ("TXT", "SCRIPT"): return PreviewGenerator._text_preview(p)
            if file_type == "ZIP": return PreviewGenerator._zip_list(p)
            if file_type == "PDF": return PreviewGenerator._pdf_info(p)
        except Exception as e:
            return f"(Error generating preview: {e})"
        return "(No text preview for this file type.)"

    @staticmethod
    def _text_preview(p: Path) -> str:
        try:
            return p.read_text(encoding="utf-8", errors="replace")[:PreviewGenerator.MAX_TEXT_CHARS]
        except (IOError, UnicodeDecodeError):
            try:
                return p.read_text(encoding="latin-1", errors="replace")[:PreviewGenerator.MAX_TEXT_CHARS]
            except IOError:
                return "(Unable to read as text)"

    @staticmethod
    def _pdf_info(p: Path) -> str:
        if not PDF_OK: return "Install PyPDF2 for a basic PDF summary.\n"
        with p.open("rb") as f:
            reader = PyPDF2.PdfReader(f)
            meta = reader.metadata or {}
            return (
                f"Pages: {len(reader.pages)}\nTitle: {meta.get('/Title', 'N/A')}\nAuthor: {meta.get('/Author', 'N/A')}\n")

    @staticmethod
    def _zip_list(p: Path) -> str:
        with zipfile.ZipFile(p, "r") as zf:
            names = zf.namelist()
            head = "\n".join(names[:60])
            more = "" if len(names) <= 60 else f"\n... and {len(names) - 60} more"
            return f"{len(names)} entries:\n{head}{more}\n"


# --------------------------------##-----Main app --------#
class PolyglotCombiner:
    """The main application class."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = self._load_config()
        self._setup_window()
        self._init_state()
        self._init_style_and_theme()
        self._build_ui()
        self._update_combo_ui()
        self._refresh_all()

    def _load_config(self) -> dict:
        defaults = {"theme": "light", "last_combo_index": 0, "window_size": "1220x740"}
        if not AppConfig.CONFIG_PATH.exists(): return defaults
        try:
            config = json.loads(AppConfig.CONFIG_PATH.read_text(encoding="utf-8"))
            defaults.update({k: v for k, v in config.items() if k in defaults})
        except (json.JSONDecodeError, IOError):
            pass
        return defaults

    def _save_config(self):
        try:
            self.cfg["last_combo_index"] = self.cmb_combo.current()
            self.cfg["window_size"] = self.root.winfo_geometry()
            AppConfig.CONFIG_PATH.write_text(json.dumps(self.cfg, indent=2), encoding="utf-8")
        except (IOError, TypeError):
            pass

    def _setup_window(self):
        self.root.title(f"{AppConfig.APP_NAME} v{AppConfig.APP_VER}")
        self.root.minsize(1000, 680)
        try:
            self.root.geometry(self.cfg["window_size"])
        except tk.TclError:
            self.root.geometry("1220x740")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_state(self):
        self.primary_path: Optional[Path] = None
        self.secondary_paths: Dict[str, List[Path]] = {}
        self.strategy = "ZIP-last"
        self.output_path = tk.StringVar(value="")
        self.stub_template = tk.StringVar(value="Batch (.bat)")
        self.preview_img: Optional[ImageTk.PhotoImage] = None

    def _init_style_and_theme(self):
        self.style = ttk.Style()
        self._create_menubar()
        self._apply_current_theme()

    def _apply_current_theme(self):
        palette = Theme.get_palette(self.cfg["theme"])
        Theme.apply(self.root, self.style, palette, self.menubar)
        if hasattr(self, 'txt_stub'):
            Theme.apply_to_widget(self.txt_stub, self.cfg["theme"], "text")
            Theme.apply_to_widget(self.prev_text, self.cfg["theme"], "text")
            Theme.apply_to_widget(self.canvas, self.cfg["theme"], "canvas")
            self.zip_inspector.apply_theme(self.cfg["theme"])
            self.quick_zip.apply_theme(self.cfg["theme"])

    def _build_ui(self):
        outer = ttk.Panedwindow(self.root, orient="horizontal")
        outer.pack(fill="both", expand=True, padx=5, pady=5)
        left_frame = ttk.Frame(outer, padding=8)
        right_frame = ttk.Frame(outer, padding=8)
        outer.add(left_frame, weight=3)
        outer.add(right_frame, weight=1)
        self._create_step0_combo(left_frame)
        self._create_step1_primary(left_frame)
        self._create_step2_secondaries(left_frame)
        self._create_step3_output(left_frame)
        self._create_preview_panel(left_frame)
        self.quick_zip = QuickZipPanel(right_frame, self.cfg["theme"])
        ttk.Separator(right_frame).pack(fill="x", pady=8)
        self.zip_inspector = ZipInspectorPanel(right_frame, self.cfg["theme"])

    def _create_menubar(self):
        self.menubar = tk.Menu(self.root)
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        settings_menu.add_command(label="Preferences…", command=self._open_settings)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        self.menubar.add_command(label="Exit", command=self._on_close)
        self.root.config(menu=self.menubar)

    def _create_step0_combo(self, parent: ttk.Frame):
        step0 = ttk.Labelframe(parent, text="Step 1 — Choose combination", style=Theme.LABELFRAME_STYLE)
        step0.pack(fill="x")
        ttk.Label(step0, text="Combination:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        combo_values = [c["label"] for c in AppConfig.COMBINATIONS]
        self.cmb_combo = ttk.Combobox(step0, state="readonly", values=combo_values, width=46)
        last_idx = min(self.cfg["last_combo_index"], len(combo_values) - 1)
        self.cmb_combo.current(last_idx)
        self.cmb_combo.grid(row=0, column=1, sticky="w")
        self.cmb_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_combo())

    def _create_step1_primary(self, parent: ttk.Frame):
        self.step1 = ttk.Labelframe(parent, text="Step 2 — Primary File", style=Theme.LABELFRAME_STYLE)
        self.step1.pack(fill="x", pady=(8, 0))
        ttk.Button(self.step1, text="Choose…", command=self._pick_primary, style=Theme.BUTTON_STYLE).grid(row=0,
                                                                                                          column=0,
                                                                                                          padx=6,
                                                                                                          pady=6,
                                                                                                          sticky="w")
        self.lbl_primary = ttk.Label(self.step1, text="No file chosen", width=60, anchor="w")
        self.lbl_primary.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(self.step1, text="Clear", command=self._clear_primary, style=Theme.BUTTON_STYLE).grid(row=0,
                                                                                                         column=2,
                                                                                                         padx=6, pady=6,
                                                                                                         sticky="w")
        self.step1.columnconfigure(1, weight=1)

    def _create_step2_secondaries(self, parent: ttk.Frame):
        self.step2 = ttk.Labelframe(parent, text="Step 3 — Secondary Files", style=Theme.LABELFRAME_STYLE)
        self.step2.pack(fill="x", pady=(8, 0))
        self.sec_rows_container = ttk.Frame(self.step2)
        self.sec_rows_container.pack(fill="x", expand=True, padx=4, pady=4)

    def _create_step3_output(self, parent: ttk.Frame):
        self.step3 = ttk.Labelframe(parent, text="Step 4 — Compatibility & Output", style=Theme.LABELFRAME_STYLE)
        self.step3.pack(fill="x", pady=(8, 0))
        self.lbl_compat = ttk.Label(self.step3, text="Compatibility: —", font=("Segoe UI", 10, "bold"))
        self.lbl_compat.pack(anchor="w", padx=6, pady=(6, 0))
        self.lbl_compat_msg = ttk.Label(self.step3, text="—", wraplength=500, justify="left")
        self.lbl_compat_msg.pack(anchor="w", padx=6, pady=(0, 6))
        self.output_panel = ttk.Frame(self.step3)
        self.output_panel.pack(fill="x", padx=6, pady=(4, 8))
        self.output_panel.columnconfigure(1, weight=1)
        ttk.Label(self.output_panel, text="Output file:").grid(row=0, column=0, sticky="w")
        self.ent_output = ttk.Entry(self.output_panel, textvariable=self.output_path)
        self.ent_output.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(self.output_panel, text="Save As…", command=self._choose_output, style=Theme.BUTTON_STYLE).grid(
            row=0, column=2)
        ttk.Button(self.output_panel, text="Create", command=self._create, style=Theme.BUTTON_STYLE).grid(row=0,
                                                                                                          column=3,
                                                                                                          padx=8)
        ttk.Button(self.output_panel, text="Experiment", command=self._create_experimental,
                   style=Theme.BUTTON_STYLE).grid(row=0, column=4)
        self.stub_wrap = ttk.Labelframe(self.step3, text="Script stub (for Script + Payload)",
                                        style=Theme.LABELFRAME_STYLE)
        self.stub_wrap.pack(fill="x", padx=6, pady=(0, 8))
        top = ttk.Frame(self.stub_wrap);
        top.pack(fill="x", pady=(6, 0), padx=6)
        ttk.Label(top, text="Template:").pack(side="left")
        self.cmb_stub = ttk.Combobox(top, values=list(AppConfig.SCRIPT_TEMPLATES.keys()),
                                     textvariable=self.stub_template, state="readonly", width=18)
        self.cmb_stub.pack(side="left", padx=6)
        ttk.Button(top, text="Load", command=self._load_stub, style=Theme.BUTTON_STYLE).pack(side="left")
        ttk.Button(top, text="Clear", command=lambda: self._set_stub_text(""), style=Theme.BUTTON_STYLE).pack(
            side="left", padx=6)
        self.txt_stub = tk.Text(self.stub_wrap, height=8, wrap="word")
        self.txt_stub.pack(fill="both", expand=True, padx=6, pady=6)
        Theme.apply_to_widget(self.txt_stub, self.cfg["theme"], "text")

    def _create_preview_panel(self, parent: ttk.Frame):
        prev = ttk.Labelframe(parent, text="Preview", style=Theme.LABELFRAME_STYLE)
        prev.pack(fill="both", expand=True, pady=(8, 0))
        prev.rowconfigure(1, weight=1);
        prev.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(prev, height=250)
        self.canvas.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        Theme.apply_to_widget(self.canvas, self.cfg["theme"], "canvas")
        text_wrap = ttk.Frame(prev)
        text_wrap.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        text_wrap.rowconfigure(0, weight=1);
        text_wrap.columnconfigure(0, weight=1)
        self.prev_text = tk.Text(text_wrap, height=10, wrap="word")
        yscroll = ttk.Scrollbar(text_wrap, orient="vertical", command=self.prev_text.yview)
        self.prev_text.configure(yscrollcommand=yscroll.set, state="disabled")
        self.prev_text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        Theme.apply_to_widget(self.prev_text, self.cfg["theme"], "text")

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Preferences");
        win.transient(self.root);
        win.grab_set();
        win.resizable(False, False)
        theme_var = tk.StringVar(value=self.cfg["theme"])
        content = ttk.Frame(win, padding=10);
        content.pack(fill="both", expand=True)
        content.columnconfigure(1, weight=1)
        ttk.Label(content, text="Theme:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        theme_frame = ttk.Frame(content);
        theme_frame.grid(row=0, column=1, sticky="ew")
        ttk.Radiobutton(theme_frame, text="Light", value="light", variable=theme_var).pack(side="left", padx=5)
        ttk.Radiobutton(theme_frame, text="Dark", value="dark", variable=theme_var).pack(side="left", padx=5)
        ttk.Radiobutton(theme_frame, text="Blue & Yellow", value="blue_yellow", variable=theme_var).pack(side="left",
                                                                                                         padx=5)

        def apply_and_close():
            self.cfg["theme"] = theme_var.get()
            self._apply_current_theme()
            win.destroy()

        btn_frame = ttk.Frame(content);
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btn_frame, text="Apply", command=apply_and_close, style=Theme.BUTTON_STYLE).pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=win.destroy, style=Theme.BUTTON_STYLE).pack(side="right", padx=6)

    def _apply_combo(self):
        self._update_combo_ui(); self._refresh_all()

    def _update_combo_ui(self):
        self.primary_path = None;
        self.secondary_paths.clear()
        self.lbl_primary.config(text="No file chosen");
        self._clear_preview()
        combo = AppConfig.COMBINATIONS[self.cmb_combo.current()]
        self.strategy = combo["strategy"]
        for widget in self.sec_rows_container.winfo_children(): widget.destroy()
        sec_types = combo.get("secondaries", [])
        if not sec_types:
            ttk.Label(self.sec_rows_container, text="No secondary files are needed for this combination.").pack(
                anchor="w")
        else:
            for type_name in sec_types: self._add_secondary_row(type_name)
        is_script_combo = combo["primary"] == "SCRIPT" and self.strategy == "Script+ZIP"
        if is_script_combo:
            self.stub_wrap.pack(fill="x", padx=6, pady=(0, 8)); self._load_stub()
        else:
            self.stub_wrap.pack_forget()
        self.output_panel.pack_forget()

    def _add_secondary_row(self, type_name: str):
        row = ttk.Frame(self.sec_rows_container)
        row.pack(fill="x", pady=2);
        row.columnconfigure(1, weight=1)
        ttk.Label(row, text=f"{type_name}:", width=8).grid(row=0, column=0, sticky="w")
        var = tk.StringVar(value="— none —")
        entry = ttk.Entry(row, textvariable=var, state="readonly");
        entry.grid(row=0, column=1, sticky="ew", padx=6)

        def create_picker(tn, v): return lambda: self._pick_secondaries(tn, v)

        def create_clearer(tn, v): return lambda: self._clear_secondaries(tn, v)

        ttk.Button(row, text="Add…", command=create_picker(type_name, var), style=Theme.BUTTON_STYLE).grid(row=0,
                                                                                                           column=2)
        ttk.Button(row, text="Clear", command=create_clearer(type_name, var), style=Theme.BUTTON_STYLE).grid(row=0,
                                                                                                             column=3,
                                                                                                             padx=4)

    def _pick_primary(self):
        combo = AppConfig.COMBINATIONS[self.cmb_combo.current()]
        ptype = combo["primary"]
        fp = filedialog.askopenfilename(title=f"Select primary ({ptype})", filetypes=filters_for(ptype))
        if not fp: return
        p = Path(fp);
        actual_type = detect_type(p)
        if ptype != "ZIP" and actual_type != ptype:
            if messagebox.askyesno("Type Mismatch",
                                   f"You chose a {actual_type} file, but this combination expects {ptype}.\nSwitch to a suitable combination for {actual_type}?"):
                for i, c in enumerate(AppConfig.COMBINATIONS):
                    if c["primary"] == actual_type: self.cmb_combo.current(i); self._apply_combo(); break
                else:
                    messagebox.showinfo("Not Found", f"No primary combination found for {actual_type}."); return
        self.primary_path = p
        self.lbl_primary.config(text=f"{p.name}  [{human_size(p.stat().st_size)}]")
        self._update_preview(p);
        self._refresh_all()

    def _clear_primary(self):
        self.primary_path = None;
        self.lbl_primary.config(text="No file chosen")
        self._clear_preview();
        self._refresh_all()

    def _pick_secondaries(self, type_name: str, var: tk.StringVar):
        files = filedialog.askopenfilenames(title=f"Add {type_name} files", filetypes=filters_for(type_name))
        if not files: return
        paths = [Path(f) for f in files if Path(f).exists() and Path(f).is_file()]
        if self.primary_path: paths = [p for p in paths if p.resolve() != self.primary_path.resolve()]
        self.secondary_paths[type_name] = paths
        if paths:
            display_text = ", ".join(p.name for p in paths[:3])
            if len(paths) > 3: display_text += f" (+{len(paths) - 3} more)"
            var.set(display_text)
        else:
            var.set("— none —")
        self._refresh_all()

    def _clear_secondaries(self, type_name: str, var: tk.StringVar):
        self.secondary_paths[type_name] = [];
        var.set("— none —");
        self._refresh_all()

    def _choose_output(self):
        combo = AppConfig.COMBINATIONS[self.cmb_combo.current()]
        if self.strategy == "ZIP-last":
            ext = self.primary_path.suffix if self.primary_path else \
            AppConfig.SUPPORTED_TYPES.get(combo["primary"], [".bin"])[0]
        else:
            tmpl_map = {"Batch": ".bat", "PowerShell": ".ps1", "Python": ".py", "Bash": ".bash", "Shell": ".sh"}
            ext = next((e for key, e in tmpl_map.items() if key in self.stub_template.get()), ".sh")
        filename = filedialog.asksaveasfilename(title="Save As", defaultextension=ext,
                                                initialfile=f"polyglot_output{ext}",
                                                filetypes=[("Output", f"*{ext}"), ("All files", "*.*")])
        if filename: self.output_path.set(filename)

    def _create(self):
        combo = AppConfig.COMBINATIONS[self.cmb_combo.current()]
        if combo["primary"] != "ZIP" and not self.primary_path: messagebox.showerror("Error",
                                                                                     "A primary file must be chosen."); return
        out_str = self.output_path.get().strip()
        if not out_str: messagebox.showerror("Error", "Please choose an output file location."); return
        output_path = Path(out_str)
        try:
            payload_pairs = [(p.name, p) for paths in self.secondary_paths.values() for p in paths]
            zip_payload = FileCombiner.create_zip_payload(payload_pairs)
            if self.strategy == "ZIP-last":
                if combo["primary"] == "ZIP" and not self.primary_path:
                    output_path.write_bytes(zip_payload)
                else:
                    FileCombiner.write_zip_last(self.primary_path, zip_payload, output_path)
            else:
                stub_text = self.txt_stub.get("1.0", "end-1c")
                FileCombiner.write_script_zip(stub_text, zip_payload, output_path)
            messagebox.showinfo("Success",
                                f"Created: {output_path.name}\nSize: {human_size(output_path.stat().st_size)}")
        except (IOError, OSError, zipfile.BadZipFile) as e:
            messagebox.showerror("File Error", f"Failed to create the output file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _create_experimental(self):
        self._create()
        out_str = self.output_path.get().strip()
        if not out_str or not Path(out_str).exists(): return
        if AppConfig.COMBINATIONS[self.cmb_combo.current()]["strategy"] == "Script+ZIP":
            messagebox.showinfo("Experiment Info", "For scripts, the output file is already a dual-use polyglot.");
            return
        output_path = Path(out_str)
        zip_sibling = output_path.with_suffix(output_path.suffix + ".zip")
        try:
            shutil.copy2(output_path, zip_sibling)
            messagebox.showinfo("Experiment Complete",
                                f"A copy was created for easy ZIP inspection:\n{zip_sibling.name}")
        except (IOError, OSError) as e:
            messagebox.showerror("Experiment Failed", f"Failed to create the sibling .zip file: {e}")

    def _refresh_all(self):
        combo = AppConfig.COMBINATIONS[self.cmb_combo.current()]
        if combo["strategy"] == "ZIP-last":
            self.lbl_compat.config(text="Compatibility: High")
            self.lbl_compat_msg.config(
                text="The primary file opens normally. The extra files are contained in a trailing ZIP payload accessible with an archive tool.")
        else:
            self.lbl_compat.config(text="Compatibility: Dual-Use (Script/ZIP)")
            self.lbl_compat_msg.config(
                text="The file runs as a script. The same file can also be opened with an archive tool to access the payload.")
        if self.primary_path or combo["primary"] == "ZIP":
            self.output_panel.pack(fill="x", padx=6, pady=(4, 8))
        else:
            self.output_panel.pack_forget()

    def _load_stub(self):
        self._set_stub_text(AppConfig.SCRIPT_TEMPLATES.get(self.stub_template.get(), "# No template found"))

    def _set_stub_text(self, text: str):
        self.txt_stub.delete("1.0", "end"); self.txt_stub.insert("1.0", text)

    def _update_preview(self, path: Path):
        self._clear_preview()
        if PIL_OK and detect_type(path) in ("JPEG", "PNG", "GIF"):
            try:
                with Image.open(path) as img:
                    img.thumbnail((self.canvas.winfo_width() or 900, 250))
                    self.preview_img = ImageTk.PhotoImage(img)
                    self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                                             anchor="center", image=self.preview_img)
            except Exception:
                pass
        preview_content = PreviewGenerator.get_text_preview(path)
        self.prev_text.config(state="normal");
        self.prev_text.delete("1.0", "end")
        self.prev_text.insert("1.0", preview_content);
        self.prev_text.config(state="disabled")

    def _clear_preview(self):
        self.preview_img = None;
        self.canvas.delete("all")
        self.prev_text.config(state="normal");
        self.prev_text.delete("1.0", "end");
        self.prev_text.config(state="disabled")

    def _on_close(self):
        self._save_config(); self.root.destroy()


# --------------------------------##-----UI Panels (Refactored) --------#
class QuickZipPanel(ttk.Frame):
    def __init__(self, parent, theme_name: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_name = theme_name;
        self._build()

    def _build(self):
        ttk.Label(self, text="Quick ZIP", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(self, text="Create a standard ZIP archive from files.").pack(anchor="w", pady=(0, 6))
        self.lb_zip = tk.Listbox(self, height=8, selectmode="extended")
        self.lb_zip.pack(fill="x", expand=False)
        self.apply_theme(self.theme_name)
        btn_frame = ttk.Frame(self);
        btn_frame.pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Add…", command=self._add_files, style=Theme.BUTTON_STYLE).pack(side="left")
        ttk.Button(btn_frame, text="Remove", command=self._remove_selected, style=Theme.BUTTON_STYLE).pack(side="left",
                                                                                                           padx=6)
        ttk.Button(btn_frame, text="Create ZIP…", command=self._create_zip, style=Theme.BUTTON_STYLE).pack(side="left")
        self.pack(fill="x")

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name; Theme.apply_to_widget(self.lb_zip, self.theme_name, "listbox")

    def _add_files(self):
        files = filedialog.askopenfilenames(title="Add files to ZIP", filetypes=AppConfig.FILE_FILTERS_ALL)
        for f in files: self.lb_zip.insert("end", f)

    def _remove_selected(self):
        for i in reversed(self.lb_zip.curselection()): self.lb_zip.delete(i)

    def _create_zip(self):
        items = self.lb_zip.get(0, "end")
        if not items: messagebox.showwarning("Empty", "No files to zip."); return
        target = filedialog.asksaveasfilename(title="Create ZIP", defaultextension=".zip", initialfile="archive.zip",
                                              filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")])
        if not target: return
        try:
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for f in items:
                    p = Path(f)
                    if p.is_file(): zf.write(p, p.name)
            messagebox.showinfo("Success", f"ZIP created: {Path(target).name}")
        except (IOError, OSError, zipfile.BadZipFile) as e:
            messagebox.showerror("Error", f"Failed to create ZIP: {e}")


class ZipInspectorPanel(ttk.Frame):
    COLUMNS = ("name", "size", "packed", "ratio", "modified")

    def __init__(self, parent, theme_name: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme_name = theme_name;
        self.zip_path: Optional[Path] = None;
        self._build()

    def _build(self):
        ttk.Label(self, text="Inspect ZIP", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        bar = ttk.Frame(self);
        bar.pack(fill="x", pady=(4, 4))
        ttk.Button(bar, text="Open ZIP…", command=self._open_zip, style=Theme.BUTTON_STYLE).pack(side="left")
        ttk.Button(bar, text="Close", command=self._close_zip, style=Theme.BUTTON_STYLE).pack(side="left", padx=6)
        self.lbl_zip_name = ttk.Label(bar, text="— No file loaded —");
        self.lbl_zip_name.pack(side="left", padx=6)
        tree_frame = ttk.Frame(self);
        tree_frame.pack(fill="both", expand=True)
        tree_frame.rowconfigure(0, weight=1);
        tree_frame.columnconfigure(0, weight=1)
        self.tv_inspect = ttk.Treeview(tree_frame, columns=self.COLUMNS, show="headings", height=12)
        for col, width, stretch in [("name", 260, True), ("size", 90, False), ("packed", 90, False),
                                    ("ratio", 70, False), ("modified", 140, False)]:
            self.tv_inspect.heading(col, text=col.title());
            self.tv_inspect.column(col, width=width, anchor="w", stretch=stretch)
        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tv_inspect.yview)
        self.tv_inspect.configure(yscrollcommand=yscroll.set)
        self.tv_inspect.grid(row=0, column=0, sticky="nsew");
        yscroll.grid(row=0, column=1, sticky="ns")
        self._create_context_menu();
        self.pack(fill="both", expand=True)

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name  # Treeview is themed centrally

    def _create_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        palette = Theme.get_palette(self.theme_name)  # Theme the context menu
        self.menu.config(bg=palette["menu_bg"], fg=palette["menu_fg"], activebackground=palette["menu_active_bg"],
                         activeforeground=palette["menu_active_fg"], relief='flat')
        self.menu.add_command(label="Extract selected…", command=self._extract_selected)
        self.menu.add_command(label="Delete selected", command=self._delete_selected)
        self.menu.add_separator()
        self.menu.add_command(label="Refresh", command=lambda: self.zip_path and self._load_entries(self.zip_path))
        self.tv_inspect.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))

    def _open_zip(self):
        fp = filedialog.askopenfilename(title="Open ZIP to inspect",
                                        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")])
        if not fp: return
        self.zip_path = Path(fp);
        self.lbl_zip_name.config(text=self.zip_path.name);
        self._load_entries(self.zip_path)

    def _close_zip(self):
        self.zip_path = None;
        self.lbl_zip_name.config(text="— No file loaded —")
        self.tv_inspect.delete(*self.tv_inspect.get_children())

    def _load_entries(self, zpath: Path):
        self.tv_inspect.delete(*self.tv_inspect.get_children())
        try:
            with zipfile.ZipFile(zpath, "r") as zf:
                for info in zf.infolist():
                    size = info.file_size;
                    csize = info.compress_size
                    ratio = "0%" if size == 0 else f"{int(100 * (1 - csize / size))}%"
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", info.date_time + (0, 0, -1))
                    values = (info.filename, human_size(size), human_size(csize), ratio, mod_time)
                    self.tv_inspect.insert("", "end", values=values)
        except (zipfile.BadZipFile, FileNotFoundError, PermissionError) as e:
            messagebox.showerror("Error", f"Failed to read ZIP file:\n{e}");
            self._close_zip()

    def _get_selected_filenames(self) -> List[str]:
        return [self.tv_inspect.item(iid, "values")[0] for iid in self.tv_inspect.selection()]

    def _extract_selected(self):
        if not self.zip_path: return
        names = self._get_selected_filenames()
        if not names: messagebox.showwarning("Selection Empty", "Select entries to extract."); return
        outdir = filedialog.askdirectory(title="Extract to folder", initialdir=self.zip_path.parent)
        if not outdir: return
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                zf.extractall(outdir, members=names)
            messagebox.showinfo("Success", f"Extracted {len(names)} item(s) to:\n{outdir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract: {e}")

    def _delete_selected(self):
        if not self.zip_path: return
        names_to_remove = set(self._get_selected_filenames())
        if not names_to_remove: messagebox.showwarning("Selection Empty", "Select entries to delete."); return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Permanently delete {len(names_to_remove)} item(s) from {self.zip_path.name}?"): return
        tmp_path = self.zip_path.with_suffix(self.zip_path.suffix + ".tmp")
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf_in, zipfile.ZipFile(tmp_path, "w",
                                                                               compression=zipfile.ZIP_DEFLATED) as zf_out:
                zf_out.comment = zf_in.comment
                for item in zf_in.infolist():
                    if item.filename not in names_to_remove: zf_out.writestr(item, zf_in.read(item.filename))
            shutil.move(tmp_path, self.zip_path)
            self._load_entries(self.zip_path)
        except Exception as e:
            if tmp_path.exists(): tmp_path.unlink()
            messagebox.showerror("Error", f"Failed to delete items: {e}")


# --------------------------------##-----main --------#
def main():
    """Initializes and runs the application."""
    root = tk.Tk()
    app = PolyglotCombiner(root)
    root.mainloop()


if __name__ == "__main__":
    main()
