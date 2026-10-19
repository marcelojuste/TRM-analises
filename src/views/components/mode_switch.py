import customtkinter as ctk


class AnimatedModeSwitch(ctk.CTkFrame):

    def __init__(self, master, on_mode_changed=None, **kwargs):
        super().__init__(master, fg_color="transparent", height=38, **kwargs)
        self.on_mode_changed = on_mode_changed
        self.is_sped = True

        self._build_switch()

    def _build_switch(self):
        self.bg_frame = ctk.CTkFrame(
            self,
            fg_color="#DBEAFE",
            corner_radius=19,
            border_width=1,
            border_color="#BFDBFE",
            height=38
        )
        self.bg_frame.pack(fill="both", expand=True)

        self.lbl_sintegra = ctk.CTkLabel(
            self.bg_frame,
            text="SINTEGRA",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#94A3B8"
        )
        self.lbl_sintegra.pack(side="left", padx=(14, 6))

        self.switch_control = ctk.CTkSwitch(
            self.bg_frame,
            text="",
            width=46,
            height=24,
            switch_width=44,
            switch_height=22,
            progress_color="#2563EB",
            button_color="#FFFFFF",
            button_hover_color="#F8FAFC",
            command=self._on_switch_toggled
        )
        self.switch_control.pack(side="left", padx=2)
        self.switch_control.select()

        self.lbl_sped = ctk.CTkLabel(
            self.bg_frame,
            text="SPED",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#1D4ED8"
        )
        self.lbl_sped.pack(side="left", padx=(6, 14))

    def _on_switch_toggled(self):
        self.is_sped = bool(self.switch_control.get())
        self._update_colors()

        if self.on_mode_changed and callable(self.on_mode_changed):
            self.on_mode_changed(self.is_sped)

    def _update_colors(self):
        if self.is_sped:
            self.bg_frame.configure(fg_color="#DBEAFE", border_color="#BFDBFE")
            self.switch_control.configure(progress_color="#2563EB")
            self.lbl_sped.configure(text_color="#1D4ED8")
            self.lbl_sintegra.configure(text_color="#94A3B8")
        else:
            self.bg_frame.configure(fg_color="#FFEDD5", border_color="#FED7AA")
            self.switch_control.configure(progress_color="#EA580C")
            self.lbl_sintegra.configure(text_color="#C2410C")
            self.lbl_sped.configure(text_color="#94A3B8")

    def set_enabled(self, enabled: bool):
        self.switch_control.configure(state="normal" if enabled else "disabled")