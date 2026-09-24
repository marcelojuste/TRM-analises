import customtkinter as ctk
from tkinter import filedialog

class FileSelectionCard(ctk.CTkFrame):
    def __init__(self, master, title: str, is_directory: bool = False, **kwargs):
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
        self.selected_path = ""

        self._build_widgets()

    def _build_widgets(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(16, 12))

        self.title_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_left.pack(side="left")

        self.lbl_icon = ctk.CTkLabel(
            self.title_left, 
            text="📄", 
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

        placeholder = "Nenhuma pasta selecionada..." if self.is_directory else "Nenhum arquivo selecionado..."
        btn_text = "Selecionar Pasta" if self.is_directory else "Selecionar Arquivo"

        self.entry_path = ctk.CTkEntry(
            self.action_frame,
            placeholder_text=placeholder,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color="#FFFFFF",
            border_color="#CBD5E1",
            border_width=1,
            text_color="#334155",
            placeholder_text_color="#94A3B8",
            corner_radius=8,
            height=38
        )
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_path.configure(state="readonly")

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

    def _open_dialog(self):
        if self.is_directory:
            path = filedialog.askdirectory(title=f"Selecionar Pasta para {self.title}")
        else:
            path = filedialog.askopenfilename(
                title=f"Selecionar Ficheiro para {self.title}",
                filetypes=[("Documentos Fiscais", "*.xml *.txt"), ("Todos os Ficheiros", "*.*")]
            )

        if path:
            self.selected_path = path
            self.entry_path.configure(state="normal")
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, path)
            self.entry_path.configure(state="readonly")

            self.lbl_status.configure(text="Selecionado", fg_color="#DCFCE7", text_color="#15803D")

    def get_path(self) -> str:
        return self.selected_path