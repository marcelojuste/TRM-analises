from pathlib import Path
from tkinter import filedialog
from typing import List
import customtkinter as ctk

from src.views.components.file_card.file_card_base import BaseSelectionCard
from src.views.components.hover_button import HoverRemoveButton


class FiscalFileSelectionCard(BaseSelectionCard):

    def __init__(self, master, is_sped: bool = True, **kwargs):
        self.is_sped = is_sped
        title = "Arquivos Fiscais SPED (.txt)" if is_sped else "Arquivo Fiscal Sintegra (.txt)"
        super().__init__(master, title=title, icon="📄", **kwargs)

    def set_mode(self, is_sped: bool):
        self.is_sped = is_sped
        new_title = "Arquivos Fiscais SPED (.txt)" if is_sped else "Arquivo Fiscal Sintegra (.txt)"
        self.lbl_title.configure(text=new_title)

        if not self.is_sped and len(self.selected_paths) > 1:
            self.selected_paths = self.selected_paths[:1]
            self._render_items()
            self._notify_change()

    def add_paths(self, paths: List[Path]):
        max_allowed = 2 if self.is_sped else 1
        added = False

        for path in paths:
            if path and path.is_file() and path.suffix.lower() == ".txt":
                if path not in self.selected_paths and len(self.selected_paths) < max_allowed:
                    self.selected_paths.append(path)
                    added = True

        if added:
            self._render_items()
            self._notify_change()

    def add_path(self, path: Path):
        self.add_paths([path])

    def _reset_grid(self):
        for r in range(2):
            self.items_container.grid_rowconfigure(r, weight=0, uniform="")
        for c in range(2):
            self.items_container.grid_columnconfigure(c, weight=0, uniform="")

    def _render_items(self):
        for w in self.items_container.winfo_children():
            w.destroy()

        self._reset_grid()

        num_items = len(self.selected_paths)
        if num_items == 0:
            self._render_empty_state()
            return

        self.items_container.grid_rowconfigure(0, weight=1)
        for c in range(num_items):
            self.items_container.grid_columnconfigure(c, weight=1, uniform="fiscal_col")

        for idx, path in enumerate(self.selected_paths):
            item_frame = ctk.CTkFrame(
                self.items_container,
                fg_color="#EFF6FF",
                border_color="#BFDBFE",
                border_width=1,
                corner_radius=8
            )
            item_frame.grid(row=0, column=idx, padx=3, pady=3, sticky="nsew")
            self._setup_drag_and_drop(item_frame)

            lbl_icon = ctk.CTkLabel(
                item_frame, text="📄", font=ctk.CTkFont(size=13), text_color="#2563EB"
            )
            lbl_icon.pack(side="left", padx=(8, 4))

            btn_remove = HoverRemoveButton(
                item_frame, command=lambda p=path: self.remove_path(p)
            )
            btn_remove.pack(side="right", padx=(4, 6))

            file_display = path.name
            if len(file_display) > 22:
                file_display = file_display[:10] + "..." + file_display[-9:]

            lbl_path = ctk.CTkLabel(
                item_frame,
                text=file_display,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="#1E40AF",
                anchor="w"
            )
            lbl_path.pack(side="left", fill="x", expand=True, padx=2)

    def _on_add_clicked(self):
        max_allowed = 2 if self.is_sped else 1
        if len(self.selected_paths) >= max_allowed:
            return

        raw_selection = filedialog.askopenfilenames(
            title="Selecionar Arquivo(s) Fiscal(ais) (.txt)",
            filetypes=[("Arquivos Fiscais", "*.txt"), ("Todos os Arquivos", "*.*")]
        )

        if not raw_selection:
            return

        parsed_paths = []
        if isinstance(raw_selection, (list, tuple)):
            parsed_paths = [Path(p) for p in raw_selection]
        elif isinstance(raw_selection, str):
            split_list = self.winfo_toolkit().tk.splitlist(raw_selection)
            parsed_paths = [Path(p) for p in split_list]

        if parsed_paths:
            self.add_paths(parsed_paths)