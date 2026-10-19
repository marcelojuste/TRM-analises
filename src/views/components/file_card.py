from pathlib import Path
from tkinter import filedialog
from typing import Callable, List, Optional
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES
    HAS_TKINTER_DND = True
except ImportError:
    HAS_TKINTER_DND = False


class HoverRemoveButton(ctk.CTkButton):
    """Botão de remoção personalizado (X) que escurece o vermelho ao passar o mouse."""

    def __init__(self, master, command=None, **kwargs):
        super().__init__(
            master,
            text="✕",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color="#FEE2E2",
            text_color="#EF4444",
            hover_color="#DC2626",
            width=26,
            height=26,
            corner_radius=13,
            command=command,
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(text_color="#FFFFFF")

    def _on_leave(self, event):
        self.configure(text_color="#EF4444")


class BaseSelectionCard(ctk.CTkFrame):
    """Card expansível com suporte para drag and drop e distribuição 1/N de arquivos."""

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
            fg_color="#F1F5F9",
            border_color="#CBD5E1",
            border_width=1,
            corner_radius=12,
            height=180,
            **kwargs
        )
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
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#0F172A"
        )
        self.lbl_title.pack(side="left")

        self.btn_add = ctk.CTkButton(
            self.header_frame,
            text="＋",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
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
        self.items_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
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
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#94A3B8"
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
        """Renderiza os arquivos ocupando 1/N do espaço vertical disponível do container."""
        for w in self.items_container.winfo_children():
            w.destroy()

        num_items = len(self.selected_paths)
        if num_items == 0:
            self._render_empty_state()
            return

        for i in range(num_items):
            self.items_container.grid_rowconfigure(i, weight=1, uniform="item_row")
        self.items_container.grid_columnconfigure(0, weight=1)

        for idx, path in enumerate(self.selected_paths):
            item_frame = ctk.CTkFrame(
                self.items_container,
                fg_color="#FFFFFF",
                border_color="#CBD5E1",
                border_width=1,
                corner_radius=8
            )
            item_frame.grid(row=idx, column=0, sticky="nsew", pady=2)
            self._setup_drag_and_drop(item_frame)

            icon_item = "📁" if path.is_dir() else "📄"
            lbl_icon = ctk.CTkLabel(
                item_frame, text=icon_item, font=ctk.CTkFont(size=12), text_color="#64748B"
            )
            lbl_icon.pack(side="left", padx=(10, 6))

            lbl_path = ctk.CTkLabel(
                item_frame,
                text=path.name or str(path),
                font=ctk.CTkFont(family="Inter", size=11, weight="medium"),
                text_color="#334155",
                anchor="w"
            )
            lbl_path.pack(side="left", fill="x", expand=True, padx=4)

            btn_remove = HoverRemoveButton(
                item_frame, command=lambda p=path: self.remove_path(p)
            )
            btn_remove.pack(side="right", padx=6)

    def _notify_change(self):
        if self.on_change and callable(self.on_change):
            self.on_change(self.selected_paths)

    def _on_add_clicked(self):
        raise NotImplementedError

    def get_paths(self) -> List[Path]:
        return self.selected_paths

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_add.configure(state=state)


class XMLSelectionCard(BaseSelectionCard):

    def __init__(self, master, **kwargs):
        super().__init__(master, title="Diretórios de XMLs (NF-e / NFC-e)", icon="📁", **kwargs)

    def add_path(self, path: Path):
        if path and path.is_dir() and path not in self.selected_paths:
            self.selected_paths.append(path)
            self._render_items()
            self._notify_change()

    def _on_add_clicked(self):
        chosen_dir = filedialog.askdirectory(title="Selecionar Pasta de XMLs")
        if chosen_dir:
            self.add_path(Path(chosen_dir))


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

    def add_path(self, path: Path):
        max_allowed = 2 if self.is_sped else 1

        if path and path.is_file() and path.suffix.lower() == ".txt":
            if path not in self.selected_paths:
                if len(self.selected_paths) >= max_allowed:
                    self.selected_paths[-1] = path
                else:
                    self.selected_paths.append(path)

                self._render_items()
                self._notify_change()

    def _on_add_clicked(self):
        max_allowed = 2 if self.is_sped else 1
        if len(self.selected_paths) >= max_allowed:
            return

        chosen_file = filedialog.askopenfilename(
            title="Selecionar Arquivo Fiscal (.txt)",
            filetypes=[("Arquivos Fiscais", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if chosen_file:
            self.add_path(Path(chosen_file))