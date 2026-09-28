"""Minimal accessible Tkinter screen for Playlist Music."""

import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from playlist_music.csv_mapping_dialog import show_csv_mapping_dialog
from playlist_music.imports import (
    parse_json_file,
    parse_m3u_file,
    parse_txt_file,
    preview_csv_file,
)
from playlist_music.models import CsvColumnMapping, QueueProgress, TrackRequest
from playlist_music.service import ServiceResult, create_playlist, retry_failed_playlist
from playlist_music.ui_state import InputState, completion_actions, progress_item_details, safe_output_path
from playlist_music.worker import PlaylistWorker


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
        self.progress_current = tk.StringVar()
        self.progress_summary = tk.StringVar()
        self.worker = PlaylistWorker()
        self.advanced_frame: ttk.LabelFrame | None = None
        self.frame: ttk.Frame | None = None
        self._active_output_folder: Path | None = None
        self._active_playlist_name = ""
        self._folder_to_open: Path | None = None
        self._playlist_to_open: Path | None = None
        self._last_result: ServiceResult | None = None
        self.create_button: ttk.Button | None = None
        self.progress_frame: ttk.LabelFrame | None = None
        self.progress_bar: ttk.Progressbar | None = None
        self.progress_tree: ttk.Treeview | None = None
        self._active_requests: list[TrackRequest] = []
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
        self.create_button = ttk.Button(frame, text="Create playlist", command=self._create_playlist)
        self.create_button.grid(
            row=13, pady=(16, 8), sticky="w"
        )
        ttk.Label(frame, textvariable=self.status, wraplength=560).grid(row=14, sticky="w")
        self.progress_frame = ttk.LabelFrame(frame, text="Download progress", padding=8)
        self.progress_frame.grid(row=15, pady=(12, 0), sticky="ew")
        self.progress_frame.columnconfigure(0, weight=1)
        ttk.Label(self.progress_frame, textvariable=self.progress_current).grid(row=0, sticky="w")
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="determinate", maximum=1)
        self.progress_bar.grid(row=1, pady=(6, 4), sticky="ew")
        ttk.Label(self.progress_frame, textvariable=self.progress_summary).grid(row=2, sticky="w")
        self.progress_tree = ttk.Treeview(
            self.progress_frame,
            columns=("track", "status", "detail"),
            show="headings",
            height=5,
        )
        self.progress_tree.heading("track", text="Track")
        self.progress_tree.heading("status", text="Status")
        self.progress_tree.heading("detail", text="Details")
        self.progress_tree.column("track", width=190, stretch=True)
        self.progress_tree.column("status", width=85, stretch=False)
        self.progress_tree.column("detail", width=275, stretch=True)
        self.progress_tree.grid(row=3, pady=(8, 0), sticky="ew")
        self.progress_frame.grid_remove()
        self.actions_frame = ttk.Frame(frame)
        self.actions_frame.grid(row=16, pady=(12, 0), sticky="w")
        self.open_folder_button = ttk.Button(
            self.actions_frame, text="Open folder", command=self._open_folder, state="disabled"
        )
        self.open_folder_button.grid(row=0, column=0)
        self.open_playlist_button = ttk.Button(
            self.actions_frame, text="Open playlist", command=self._open_playlist, state="disabled"
        )
        self.open_playlist_button.grid(row=0, column=1, padx=(8, 0))
        self.retry_button = ttk.Button(
            self.actions_frame,
            text="Retry failed downloads",
            command=self._retry_failed,
            state="disabled",
        )
        self.retry_button.grid(row=0, column=2, padx=(8, 0))
        self.actions_frame.grid_remove()

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
        if path.suffix.lower() == ".csv":
            preview = preview_csv_file(path)
            if preview.error:
                self.status.set(preview.error)
                return
            show_csv_mapping_dialog(self.root, preview, lambda mapping: self._apply_csv_mapping(path, mapping))
            return
        parser = {
            ".txt": parse_txt_file,
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

    def _apply_csv_mapping(self, path: Path, mapping: CsvColumnMapping) -> str | None:
        error = self.state.apply_csv_mapping(path, mapping)
        if error:
            return error
        self.summary.set(self.state.import_summary)
        self.status.set(f"Imported {path.name}.")
        return None

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
            self.advanced_frame.grid(row=17, pady=(12, 0), sticky="ew")
            ttk.Label(
                self.advanced_frame,
                text="Metadata, duplicate handling, and opening the folder use safe defaults.",
            ).grid(sticky="w")
        elif self.advanced_frame:
            self.advanced_frame.destroy()
            self.advanced_frame = None

    def _create_playlist(self) -> None:
        if not self.state.output_folder:
            self.status.set("Choose an output folder first.")
            return
        playlist_name = self.name.get()
        output_folder = self.state.output_folder
        imported = self.state.imported
        quality = self.state.quality
        started = self.worker.start(
            lambda on_progress: create_playlist(
                playlist_name,
                output_folder,
                imported,
                quality=quality,
                embed_metadata=self.state.embed_metadata,
                embed_thumbnail=self.state.embed_thumbnail,
                skip_duplicates=self.state.skip_duplicates,
                on_progress=on_progress,
            )
        )
        if not started:
            self.status.set("A playlist is already being created.")
            return
        if self.create_button:
            self.create_button.configure(state="disabled")
        self._active_output_folder = output_folder
        self._active_playlist_name = playlist_name
        self._active_requests = list(imported.requests)
        self._start_progress()
        self.actions_frame.grid_remove()
        self.root.after(50, self._poll_worker)

    def _poll_worker(self) -> None:
        for event in self.worker.drain_events():
            if event.kind == "progress" and event.progress:
                self._show_progress(event.progress)
            elif event.kind == "completed" and event.result:
                self._show_completion(event.result)
            elif event.kind == "error":
                self._show_error(event.message)
        if self.worker.is_running:
            self.root.after(50, self._poll_worker)

    def _enable_creation(self) -> None:
        if self.create_button:
            self.create_button.configure(state="normal")

    def _start_progress(self) -> None:
        total = len(self._active_requests)
        if not self.progress_frame or not self.progress_bar or not self.progress_tree:
            return
        self.progress_frame.grid()
        self.progress_bar.configure(maximum=max(total, 1), value=0)
        for row in self.progress_tree.get_children():
            self.progress_tree.delete(row)
        self.progress_summary.set(f"0 of {total} complete")
        self.progress_current.set(self._current_track_label(0, total))
        self.status.set("Playlist creation started.")

    def _show_progress(self, progress: QueueProgress) -> None:
        if not self.progress_bar or not self.progress_tree:
            return
        status, detail = progress_item_details(progress)
        self.progress_bar.configure(value=progress.completed)
        self.progress_tree.insert("", "end", values=(progress.item.request.query, status, detail))
        self.progress_summary.set(f"{progress.completed} of {progress.total} complete")
        self.progress_current.set(self._current_track_label(progress.completed, progress.total))
        self.status.set(f"{status}: {progress.item.request.query}")

    def _retry_failed(self) -> None:
        if not self._last_result:
            return
        failed = [item.request for item in self._last_result.queue.items if item.status == "failed"] if self._last_result.queue else []
        if not failed:
            self.status.set("There are no failed downloads to retry.")
            return
        started = self.worker.start(
            lambda on_progress: retry_failed_playlist(
                self._active_playlist_name,
                self._last_result,
                quality=self.state.quality,
                embed_metadata=self.state.embed_metadata,
                embed_thumbnail=self.state.embed_thumbnail,
                on_progress=on_progress,
            )
        )
        if not started:
            self.status.set("A playlist is already being created.")
            return
        self._active_requests = failed
        self.retry_button.configure(state="disabled")
        self.actions_frame.grid_remove()
        self._start_progress()
        self.root.after(50, self._poll_worker)

    def _current_track_label(self, completed: int, total: int) -> str:
        if completed >= total:
            return "Finishing playlist…"
        request = self._active_requests[completed]
        return f"Downloading {completed + 1} of {total}: {request.query}"

    def _show_completion(self, result: ServiceResult) -> None:
        self._last_result = result
        actions = completion_actions(result, self._active_output_folder or self.state.output_folder)
        self.status.set(actions.message)
        self._folder_to_open = actions.folder
        self._playlist_to_open = actions.playlist
        self.open_folder_button.configure(state="normal" if actions.folder else "disabled")
        self.open_playlist_button.configure(state="normal" if actions.playlist else "disabled")
        failed = bool(result.queue and any(item.status == "failed" for item in result.queue.items))
        self.retry_button.configure(state="normal" if failed else "disabled")
        if actions.folder or actions.playlist or failed:
            self.actions_frame.grid()
        else:
            self.actions_frame.grid_remove()
        self._enable_creation()

    def _show_error(self, message: str | None) -> None:
        self.status.set(message or "Playlist creation failed unexpectedly.")
        self.actions_frame.grid_remove()
        self._enable_creation()

    def _open_folder(self) -> None:
        self._open_path(self._folder_to_open, directory=True)

    def _open_playlist(self) -> None:
        self._open_path(self._playlist_to_open, directory=False)

    def _open_path(self, candidate: Path | None, *, directory: bool) -> None:
        path = safe_output_path(self._active_output_folder or self.state.output_folder, candidate, directory=directory)
        if not path:
            self.status.set("That output is no longer available.")
            return
        try:
            os.startfile(str(path))
        except OSError:
            self.status.set("Could not open the selected output.")


def run_app() -> None:
    """Open the local Playlist Music window."""
    root = tk.Tk()
    PlaylistMusicApp(root)
    root.mainloop()
