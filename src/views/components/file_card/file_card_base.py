from pathlib import Path
from typing import Callable, List, Optional
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES
    HAS_TKINTER_DND = True
except ImportError:
    HAS_TKINTER_DND = False


class BaseSelectionCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        title: str,
        icon: str = "📁",
        on_change: Optional[Callable[[List[Path]], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            border_width=1,
            corner_radius=12,
            height=190,
            **kwargs
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.title_text = title
        self.icon_symbol = icon
        self.on_change = on_change
        self.selected_paths: List[Path] = []

        self._build_header()
        self._build_content_area()
        self._setup_drag_and_drop(self)

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(12, 8))

        self.title_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_left.pack(side="left")

        self.lbl_icon = ctk.CTkLabel(
            self.title_left,
            text=self.icon_symbol,
            font=ctk.CTkFont(size=15),
            text_color="#2563EB"
        )
        self.lbl_icon.pack(side="left", padx=(0, 6))

        self.lbl_title = ctk.CTkLabel(
            self.title_left,
            text=self.title_text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#0F172A"
        )
        self.lbl_title.pack(side="left")

        self.btn_add = ctk.CTkButton(
            self.header_frame,
            text="＋",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            width=28,
            height=28,
            corner_radius=14,
            command=self._on_add_clicked
        )
        self.btn_add.pack(side="right")

    def _build_content_area(self):
        self.items_container = ctk.CTkFrame(self, fg_color="transparent")
        self.items_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._setup_drag_and_drop(self.items_container)
        self._render_empty_state()

    def _setup_drag_and_drop(self, widget):
        if HAS_TKINTER_DND:
            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._handle_drop)
            except Exception:
                pass

    def _handle_drop(self, event):
        raw_data = event.data
        if not raw_data:
            return

        paths = self.winfo_toolkit().tk.splitlist(raw_data)
        for p_str in paths:
            clean_p = p_str.strip("{}").strip('"')
            self.add_path(Path(clean_p))

    def _render_empty_state(self):
        for w in self.items_container.winfo_children():
            w.destroy()

        self.lbl_empty = ctk.CTkLabel(
            self.items_container,
            text="Arraste os arquivos/pastas para aqui\nou clique no botão ＋",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B"
        )
        self.lbl_empty.pack(expand=True, fill="both")
        self._setup_drag_and_drop(self.lbl_empty)

    def add_path(self, path: Path):
        if path and path.exists() and path not in self.selected_paths:
            self.selected_paths.append(path)
            self._render_items()
            self._notify_change()

    def remove_path(self, path: Path):
        if path in self.selected_paths:
            self.selected_paths.remove(path)
            if self.selected_paths:
                self._render_items()
            else:
                self._render_empty_state()
            self._notify_change()

    def clear_selection(self):
        self.selected_paths.clear()
        self._render_empty_state()
        self._notify_change()

    def _render_items(self):
        raise NotImplementedError

    def _notify_change(self):
        if self.on_change and callable(self.on_change):
            self.on_change(self.selected_paths)

    def _on_add_clicked(self):
        raise NotImplementedError

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_add.configure(state=state)