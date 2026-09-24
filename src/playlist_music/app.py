"""Minimal accessible Tkinter screen for Playlist Music."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from playlist_music.imports import (
    parse_csv_file,
    parse_json_file,
    parse_m3u_file,
    parse_txt_file,
)
from playlist_music.ui_state import InputState


class PlaylistMusicApp:
    """A small form that collects the first playlist choices."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.state = InputState()
        self.name = tk.StringVar()
        self.folder = tk.StringVar()
        self.quality = tk.StringVar(value=self.state.quality)
        self.summary = tk.StringVar(value=self.state.import_summary)
        self.status = tk.StringVar(value="Choose a playlist name, songs, and a folder.")
        self.advanced_frame: ttk.LabelFrame | None = None
        self.frame: ttk.Frame | None = None
        self.root.title("Playlist Music")
        self.root.minsize(620, 520)
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        self.frame = frame
        frame.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Playlist Music", font=("Segoe UI", 18, "bold")).grid(
            row=0, sticky="w"
        )
        ttk.Label(frame, text="Organize authorized music sources locally.").grid(
            row=1, pady=(0, 16), sticky="w"
        )
        ttk.Label(frame, text="Playlist name").grid(row=2, sticky="w")
        ttk.Entry(frame, textvariable=self.name).grid(row=3, pady=(0, 12), sticky="ew")
        ttk.Label(frame, text="Music queries or URLs (one per line)").grid(row=4, sticky="w")
        self.text = tk.Text(frame, height=9, wrap="word")
        self.text.grid(row=5, pady=(0, 4), sticky="ew")
        self.text.bind("<KeyRelease>", self._update_pasted_text)
        ttk.Label(frame, textvariable=self.summary).grid(row=6, pady=(0, 12), sticky="w")

        ttk.Button(frame, text="Import file", command=self._import_file).grid(row=7, sticky="w")
        ttk.Label(frame, text="Output folder").grid(row=8, pady=(12, 0), sticky="w")
        folder_frame = ttk.Frame(frame)
        folder_frame.grid(row=9, pady=(0, 12), sticky="ew")
        folder_frame.columnconfigure(0, weight=1)
        ttk.Entry(folder_frame, textvariable=self.folder).grid(row=0, column=0, sticky="ew")
        ttk.Button(folder_frame, text="Choose folder", command=self._choose_folder).grid(
            row=0, column=1, padx=(8, 0)
        )
        ttk.Label(frame, text="Audio quality").grid(row=10, sticky="w")
        quality = ttk.Combobox(
            frame,
            textvariable=self.quality,
            values=("recommended", "balanced", "compact"),
            state="readonly",
        )
        quality.grid(row=11, pady=(0, 12), sticky="w")
        quality.bind("<<ComboboxSelected>>", self._set_quality)
        ttk.Button(frame, text="More options", command=self._toggle_advanced).grid(row=12, sticky="w")
        ttk.Button(frame, text="Create playlist", command=self._create_playlist).grid(
            row=13, pady=(16, 8), sticky="w"
        )
        ttk.Label(frame, textvariable=self.status, wraplength=560).grid(row=14, sticky="w")

    def _update_pasted_text(self, _event: tk.Event) -> None:
        self.state.set_pasted_text(self.text.get("1.0", "end-1c"))
        self.summary.set(self.state.import_summary)

    def _import_file(self) -> None:
        filename = filedialog.askopenfilename(
            filetypes=[("Supported lists", "*.txt *.csv *.m3u *.m3u8 *.json")]
        )
        if not filename:
            return
        path = Path(filename)
        parser = {
            ".txt": parse_txt_file,
            ".csv": parse_csv_file,
            ".m3u": parse_m3u_file,
            ".m3u8": parse_m3u_file,
            ".json": parse_json_file,
        }.get(path.suffix.lower())
        if not parser:
            self.status.set("Choose a TXT, CSV, M3U, M3U8, or JSON file.")
            return
        self.state.set_imported(parser(path))
        self.summary.set(self.state.import_summary)
        self.status.set(f"Imported {path.name}.")

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.state.set_output_folder(Path(folder))
            self.folder.set(folder)

    def _set_quality(self, _event: tk.Event) -> None:
        self.state.set_quality(self.quality.get())

    def _toggle_advanced(self) -> None:
        self.state.toggle_advanced()
        if self.state.advanced_open:
            if not self.frame:
                return
            self.advanced_frame = ttk.LabelFrame(self.frame, text="More options", padding=8)
            self.advanced_frame.grid(row=15, pady=(12, 0), sticky="ew")
            ttk.Label(
                self.advanced_frame,
                text="Metadata, duplicate handling, and opening the folder use safe defaults.",
            ).grid(sticky="w")
        elif self.advanced_frame:
            self.advanced_frame.destroy()
            self.advanced_frame = None

    def _create_playlist(self) -> None:
        self.status.set("Playlist is ready. Background processing will be enabled next.")


def run_app() -> None:
    """Open the local Playlist Music window."""
    root = tk.Tk()
    PlaylistMusicApp(root)
    root.mainloop()
