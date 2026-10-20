import customtkinter as ctk
from PIL import Image

from src.path_manager import PATHS


class HeaderFrame(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_widgets()

    def _build_widgets(self):
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", anchor="w")

        logo_path = PATHS.images_dir / "LogoTRM.png"
        if logo_path.exists():
            self.logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(48, 48),
            )
            self.logo_label = ctk.CTkLabel(
                self.left_container, text="", image=self.logo_img
            )
            self.logo_label.pack(side="left", padx=(0, 12), anchor="center")

        self.title_container = ctk.CTkFrame(
            self.left_container, fg_color="transparent"
        )
        self.title_container.pack(side="left", anchor="center")

        self.lbl_title = ctk.CTkLabel(
            self.title_container,
            text="TRM Análises",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#0F172A",
            height=26,
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            self.title_container,
            text="AUDITORIA FISCAL E ANÁLISE DE DOCUMENTOS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#2563EB",
            height=14,
        )
        self.lbl_subtitle.pack(anchor="w")

        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", anchor="e")

        self.lbl_system = ctk.CTkLabel(
            self.right_container,
            text="TRM Sistemas",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#64748B",
        )
        self.lbl_system.pack(side="right", padx=(12, 0), anchor="center")

    def update_mode_theme(self, is_sped: bool):
        if is_sped:
            self.lbl_subtitle.configure(text_color="#2563EB")
        else:
            self.lbl_subtitle.configure(text_color="#EA580C")