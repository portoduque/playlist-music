"""Small Tkinter dialog for confirming CSV column choices."""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from playlist_music.models import CsvColumnMapping, CsvPreview


def show_csv_mapping_dialog(
    parent: tk.Misc,
    preview: CsvPreview,
    on_confirm: Callable[[CsvColumnMapping], str | None],
) -> None:
    """Show a modal preview and call *on_confirm* only for a valid selection."""
    dialog = tk.Toplevel(parent)
    dialog.title("Confirm CSV columns")
    dialog.transient(parent)
    dialog.resizable(False, False)
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding=16)
    frame.grid(sticky="nsew")
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    ttk.Label(frame, text="Confirm CSV columns", font=("Segoe UI", 12, "bold")).grid(
        row=0, sticky="w"
    )
    ttk.Label(frame, text="Leave a field blank to ignore that column.").grid(
        row=1, pady=(0, 12), sticky="w"
    )

    title = tk.StringVar(value=preview.title_column or "")
    artist = tk.StringVar(value=preview.artist_column or "")
    url = tk.StringVar(value=preview.url_column or "")
    choices = ("", *preview.headers)
    selectors = (("Title", title), ("Artist", artist), ("URL", url))
    for row, (label, value) in enumerate(selectors, start=2):
        ttk.Label(frame, text=label).grid(row=row, column=0, padx=(0, 8), pady=2, sticky="w")
        ttk.Combobox(frame, textvariable=value, values=choices, state="readonly").grid(
            row=row, column=1, pady=2, sticky="ew"
        )
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Preview (first five rows)").grid(row=5, pady=(12, 4), sticky="w")
    table = ttk.Treeview(frame, columns=preview.headers, show="headings", height=max(1, len(preview.rows)))
    for header in preview.headers:
        table.heading(header, text=header)
        table.column(header, width=130, stretch=False)
    for row in preview.rows:
        table.insert("", "end", values=row)
    table.grid(row=6, columnspan=2, sticky="ew")

    message = tk.StringVar()
    ttk.Label(frame, textvariable=message, wraplength=500).grid(
        row=7, columnspan=2, pady=(8, 0), sticky="w"
    )
    buttons = ttk.Frame(frame)
    buttons.grid(row=8, columnspan=2, pady=(12, 0), sticky="e")
    confirm = ttk.Button(buttons, text="Confirm")
    confirm.grid(row=0, column=0)

    def close() -> None:
        dialog.grab_release()
        dialog.destroy()

    ttk.Button(buttons, text="Cancel", command=close).grid(row=0, column=1, padx=(8, 0))

    def mapping() -> CsvColumnMapping:
        return CsvColumnMapping(title.get() or None, artist.get() or None, url.get() or None)

    def update_confirmation(*_args: object) -> None:
        selected = [column for column in (title.get(), artist.get(), url.get()) if column]
        if not title.get() and not url.get():
            message.set("Choose Title or URL before confirming.")
            confirm.configure(state="disabled")
        elif len(selected) != len(set(selected)):
            message.set("A column can be used only once.")
            confirm.configure(state="disabled")
        else:
            message.set("")
            confirm.configure(state="normal")

    def apply() -> None:
        error = on_confirm(mapping())
        if error:
            message.set(error)
            return
        close()

    confirm.configure(command=apply)
    for value in (title, artist, url):
        value.trace_add("write", update_confirmation)
    dialog.protocol("WM_DELETE_WINDOW", close)
    dialog.bind("<Escape>", lambda _event: close())
    update_confirmation()
    dialog.focus_set()

