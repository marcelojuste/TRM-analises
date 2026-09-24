from pathlib import Path
from PIL import Image
import customtkinter as ctk

from src.app_paths import PATHS


class HeaderFrame(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_widgets()

    def _build_widgets(self):
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", anchor="w")

        self.logo_img = ctk.CTkImage(
            light_image=Image.open(PATHS.images_dir / "LogoTRM.png"),
            dark_image=Image.open(PATHS.images_dir / "LogoTRM.png"),
            size=(50, 50),
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
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color="#0F172A",
            height=26,
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            self.title_container,
            text="AUDITORIA FISCAL E ANÁLISE DE DOCUMENTOS",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color="#2B7FFF",
            height=14,
        )
        self.lbl_subtitle.pack(anchor="w")

        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", anchor="e")

        self.lbl_system = ctk.CTkLabel(
            self.right_container,
            text="TRM Sistemas",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#64748B",
        )
        self.lbl_system.pack(side="right", padx=(12, 0), anchor="center")

        self.status_badge = ctk.CTkLabel(
            self.right_container,
            text="● Auditor Atualizado",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color="#DCFCE7",
            text_color="#15803D",
            corner_radius=12,
            padx=12,
            pady=4,
        )
        self.status_badge.pack(side="right", anchor="center")