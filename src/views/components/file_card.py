from pathlib import Path
from tkinter import filedialog
from typing import Callable, List, Optional
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False


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
            fg_color="#F1F5F9",
            border_color="#E2E8F0",
            border_width=1,
            corner_radius=12,
            **kwargs
        )
        self.title_text = title
        self.icon_symbol = icon
        self.on_change = on_change
        self.selected_paths: List[Path] = []

        self._build_header()
        self._build_content_area()
        self._setup_drag_and_drop()

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(12, 8))

        self.title_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_left.pack(side="left")

        self.lbl_icon = ctk.CTkLabel(
            self.title_left,
            text=self.icon_symbol,
            font=ctk.CTkFont(size=14),
            text_color="#2B7FFF"
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
            text="＋ Adicionar",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=26,
            corner_radius=6,
            command=self._on_add_clicked
        )
        self.btn_add.pack(side="right")

    def _build_content_area(self):
        self.items_container = ctk.CTkFrame(self, fg_color="transparent")
        self.items_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._render_empty_state()

    def _setup_drag_and_drop(self):
        if HAS_DND:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self._handle_drop)
            except Exception:
                pass

    def _handle_drop(self, event):
        raw_data = event.data
        if not raw_data:
            return

        paths = self.winfo_toolkit().tk.splitlist(raw_data)
        for p_str in paths:
            self.add_path(Path(p_str.strip("{}")))

    def _render_empty_state(self):
        for widget in self.items_container.winfo_children():
            widget.destroy()

        self.lbl_empty = ctk.CTkLabel(
            self.items_container,
            text="Arraste os arquivos/pastas para aqui ou clique em '＋ Adicionar'",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#94A3B8",
            height=36
        )
        self.lbl_empty.pack(fill="x", pady=4)

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
        for widget in self.items_container.winfo_children():
            widget.destroy()

        for path in self.selected_paths:
            item_frame = ctk.CTkFrame(
                self.items_container,
                fg_color="#FFFFFF",
                border_color="#CBD5E1",
                border_width=1,
                corner_radius=6,
                height=30
            )
            item_frame.pack(fill="x", pady=2)
            item_frame.pack_propagate(False)

            icon_item = "📁" if path.is_dir() else "📄"
            lbl_icon = ctk.CTkLabel(
                item_frame, text=icon_item, font=ctk.CTkFont(size=12), text_color="#64748B"
            )
            lbl_icon.pack(side="left", padx=(8, 4))

            lbl_path = ctk.CTkLabel(
                item_frame,
                text=path.name or str(path),
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#334155",
                anchor="w"
            )
            lbl_path.pack(side="left", fill="x", expand=True, padx=4)

            btn_remove = ctk.CTkButton(
                item_frame,
                text="✕",
                font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                fg_color="transparent",
                hover_color="#FEE2E2",
                text_color="#EF4444",
                width=24,
                height=24,
                corner_radius=4,
                command=lambda p=path: self.remove_path(p)
            )
            btn_remove.pack(side="right", padx=4)

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
    """Card responsável por selecionar de 1 a N pastas de XMLs (NF-e / NFC-e)."""

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
    """Card responsável pelos arquivos fiscais .txt (Até 2 em SPED, 1 em Sintegra)."""

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