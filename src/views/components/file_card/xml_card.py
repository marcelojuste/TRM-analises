from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk

from src.views.components.file_card.file_card_base import BaseSelectionCard
from src.views.components.hover_button import HoverRemoveButton


class XMLSelectionCard(BaseSelectionCard):

    MAX_XML_DIRS = 6

    def __init__(self, master, **kwargs):
        super().__init__(master, title="Diretórios de XMLs (Até 6 pastas)", icon="📁", **kwargs)

    def add_path(self, path: Path):
        if path and path.is_dir() and path not in self.selected_paths:
            if len(self.selected_paths) < self.MAX_XML_DIRS:
                self.selected_paths.append(path)
                self._render_items()
                self._notify_change()

    def _reset_grid(self):
        for r in range(6):
            self.items_container.grid_rowconfigure(r, weight=0, uniform="")
        for c in range(6):
            self.items_container.grid_columnconfigure(c, weight=0, uniform="")

    def _render_items(self):
        for w in self.items_container.winfo_children():
            w.destroy()

        self._reset_grid()

        num_items = len(self.selected_paths)
        if num_items == 0:
            self._render_empty_state()
            return

        if num_items <= 3:
            self.items_container.grid_rowconfigure(0, weight=1)
            for c in range(num_items):
                self.items_container.grid_columnconfigure(c, weight=1, uniform="xml_col")

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
                    item_frame, text="📁", font=ctk.CTkFont(size=13), text_color="#2563EB"
                )
                lbl_icon.pack(side="left", padx=(12, 8))

                folder_name = path.name
                if len(folder_name) > 40:
                    folder_name = folder_name[:18] + "..." + folder_name[-18:]

                lbl_name = ctk.CTkLabel(
                    item_frame,
                    text=folder_name,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#1E40AF",
                    anchor="w"
                )
                lbl_name.pack(side="left", fill="x", expand=True, padx=4)

                btn_remove = HoverRemoveButton(
                    item_frame, command=lambda p=path: self.remove_path(p)
                )
                btn_remove.pack(side="right", padx=10)

        else:
            self.items_container.grid_rowconfigure((0, 1), weight=1, uniform="xml_row")
            for c in range(3):
                self.items_container.grid_columnconfigure(c, weight=1, uniform="xml_col")

            for idx, path in enumerate(self.selected_paths[:self.MAX_XML_DIRS]):
                r = idx // 3
                c = idx % 3

                item_frame = ctk.CTkFrame(
                    self.items_container,
                    fg_color="#EFF6FF",
                    border_color="#BFDBFE",
                    border_width=1,
                    corner_radius=8
                )
                item_frame.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                self._setup_drag_and_drop(item_frame)

                top_bar = ctk.CTkFrame(item_frame, fg_color="transparent")
                top_bar.pack(fill="x", padx=6, pady=(4, 0))

                lbl_icon = ctk.CTkLabel(
                    top_bar, text="📁", font=ctk.CTkFont(size=11), text_color="#2563EB"
                )
                lbl_icon.pack(side="left")

                btn_remove = HoverRemoveButton(
                    top_bar, command=lambda p=path: self.remove_path(p)
                )
                btn_remove.pack(side="right")

                folder_name = path.name
                if len(folder_name) > 24:
                    folder_name = folder_name[:11] + "..." + folder_name[-10:]

                lbl_name = ctk.CTkLabel(
                    item_frame,
                    text=folder_name,
                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                    text_color="#1E40AF",
                    anchor="center"
                )
                lbl_name.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def _on_add_clicked(self):
        if len(self.selected_paths) >= self.MAX_XML_DIRS:
            return
        chosen_dir = filedialog.askdirectory(title="Selecionar Pasta de XMLs")
        if chosen_dir:
            self.add_path(Path(chosen_dir))