import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

class FileSelectionCard(ctk.CTkFrame):
    def __init__(
        self, 
        master, 
        title: str, 
        is_directory: bool = False, 
        on_change: Optional[Callable[[str], None]] = None,
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
        
        self.title = title
        self.is_directory = is_directory
        self.on_change = on_change
        
        self.placeholder = "Nenhuma pasta selecionada..." if self.is_directory else "Nenhum arquivo selecionado..."
        self.path_var = ctk.StringVar(value="")

        self._build_widgets()

    def _build_widgets(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(16, 12))

        self.title_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_left.pack(side="left")

        self.lbl_icon = ctk.CTkLabel(
            self.title_left, 
            text="📁" if self.is_directory else "📄", 
            font=ctk.CTkFont(size=14),
            text_color="#2B7FFF"
        )
        self.lbl_icon.pack(side="left", padx=(0, 8))

        self.lbl_title = ctk.CTkLabel(
            self.title_left, 
            text=self.title, 
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#0F172A"
        )
        self.lbl_title.pack(side="left")

        self.lbl_status = ctk.CTkLabel(
            self.header_frame,
            text="Pendente",
            font=ctk.CTkFont(family="Inter", size=11),
            fg_color="#E2E8F0",
            text_color="#64748B",
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.lbl_status.pack(side="right")

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=(0, 16))

        btn_text = "Selecionar Pasta" if self.is_directory else "Selecionar Arquivo"

        self.entry_display = ctk.CTkEntry(
            self.action_frame,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            border_width=1,
            text_color="#94A3B8",
            corner_radius=8,
            height=38
        )
        self.entry_display.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_clear = ctk.CTkButton(
            self.action_frame,
            text="✕",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#FEE2E2",
            hover_color="#FCA5A5",
            text_color="#991B1B",
            width=30,
            height=38,
            corner_radius=8,
            command=self.clear_selection
        )

        self.btn_select = ctk.CTkButton(
            self.action_frame,
            text=f"📁  {btn_text}",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#0F172A",
            hover_color="#1E293B",
            text_color="#FFFFFF",
            corner_radius=8,
            height=38,
            command=self._open_dialog
        )
        self.btn_select.pack(side="right")

        self._update_ui_state("")

    def _open_dialog(self):
        if self.is_directory:
            path = filedialog.askdirectory(title=f"Selecionar Pasta para {self.title}")
        else:
            path = filedialog.askopenfilename(
                title=f"Selecionar Ficheiro para {self.title}",
                filetypes=[("Documentos Fiscais", "*.xml *.txt"), ("Todos os Ficheiros", "*.*")]
            )

        if path:
            self.set_path(path)

    def set_path(self, path: str):
        self.path_var.set(path)
        self._update_ui_state(path)
        if self.on_change and callable(self.on_change):
            self.on_change(path)

    def clear_selection(self):
        self.set_path("")

    def _update_ui_state(self, path: str):
        self.entry_display.configure(state="normal")
        self.entry_display.delete(0, "end")

        if path:
            self.entry_display.insert(0, path)
            self.entry_display.configure(text_color="#334155", state="readonly")
            self.lbl_status.configure(text="Selecionado", fg_color="#DCFCE7", text_color="#15803D")
            self.btn_clear.pack(side="left", padx=(0, 8), before=self.btn_select)
        else:
            self.entry_display.insert(0, self.placeholder)
            self.entry_display.configure(text_color="#94A3B8", state="readonly")
            self.lbl_status.configure(text="Pendente", fg_color="#E2E8F0", text_color="#64748B")
            self.btn_clear.pack_forget()

    def get_path(self) -> str:
        return self.path_var.get()

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_select.configure(state=state)
        self.btn_clear.configure(state=state)