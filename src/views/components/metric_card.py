import customtkinter as ctk

class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str = "0", subtitle: str = "", **kwargs):
        super().__init__(
            master,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
            **kwargs
        )

        self.value_var = ctk.StringVar(value=value)
        self.subtitle_var = ctk.StringVar(value=subtitle)

        self.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, padx=16, pady=(12, 2), sticky="ew")

        self.lbl_value = ctk.CTkLabel(
            self,
            textvariable=self.value_var,
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_value.grid(row=1, column=0, padx=16, pady=(0, 2), sticky="ew")

        self.lbl_subtitle = ctk.CTkLabel(
            self,
            textvariable=self.subtitle_var,
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#94A3B8",
            anchor="w"
        )
        self.lbl_subtitle.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="ew")

    def set_value(self, value: str, subtitle: str = None):
        self.value_var.set(value)
        if subtitle is not None:
            self.subtitle_var.set(subtitle)

    def reset(self, default_value: str = "0", default_subtitle: str = ""):
        self.value_var.set(default_value)
        if default_subtitle:
            self.subtitle_var.set(default_subtitle)