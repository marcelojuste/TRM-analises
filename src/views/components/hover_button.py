import customtkinter as ctk


class HoverRemoveButton(ctk.CTkButton):

    def __init__(self, master, command=None, **kwargs):
        super().__init__(
            master,
            text="✕",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#FEE2E2",
            text_color="#EF4444",
            hover_color="#DC2626",
            width=22,
            height=22,
            corner_radius=11,
            command=command,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.configure(text_color="#FFFFFF"))
        self.bind("<Leave>", lambda e: self.configure(text_color="#EF4444"))