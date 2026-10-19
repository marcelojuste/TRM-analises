import customtkinter as ctk

class MetricCard(ctk.CTkFrame):

    def __init__(self, master, title: str, **kwargs):
        super().__init__(
            master,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
            **kwargs
        )

        self.title_var = ctk.StringVar(value=title.upper())
        self.qty_var = ctk.StringVar(value="0")
        self.val_var = ctk.StringVar(value="R$ 0,00")

        self.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self,
            textvariable=self.title_var,
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="ew")

        self.values_container = ctk.CTkFrame(self, fg_color="transparent")
        self.values_container.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")
        self.values_container.grid_columnconfigure((0, 1), weight=1)

        self.lbl_qty_title = ctk.CTkLabel(
            self.values_container,
            text="QUANTIDADE",
            font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
            text_color="#94A3B8",
            anchor="w"
        )
        self.lbl_qty_title.grid(row=0, column=0, sticky="ew")

        self.lbl_qty_val = ctk.CTkLabel(
            self.values_container,
            textvariable=self.qty_var,
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_qty_val.grid(row=1, column=0, sticky="ew")

        self.lbl_val_title = ctk.CTkLabel(
            self.values_container,
            text="VALOR TOTAL",
            font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
            text_color="#94A3B8",
            anchor="w"
        )
        self.lbl_val_title.grid(row=0, column=1, sticky="ew")

        self.lbl_val_val = ctk.CTkLabel(
            self.values_container,
            textvariable=self.val_var,
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#0F172A",
            anchor="w"
        )
        self.lbl_val_val.grid(row=1, column=1, sticky="ew")

    def set_title(self, title: str):
        self.title_var.set(title.upper())

    def update_data(self, qty: int, val_cents: float):
        formatted_qty = f"{qty:,}".replace(",", ".")
        formatted_val = f"R$ {val_cents / 100.0:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.qty_var.set(formatted_qty)
        self.val_var.set(formatted_val)

    def set_border_status(self, status: str):
        if status == "MATCH":
            self.configure(border_color="#10B981")
        elif status == "MISMATCH":
            self.configure(border_color="#EF4444")
        else:
            self.configure(border_color="#E2E8F0")

    def reset(self):
        self.qty_var.set("0")
        self.val_var.set("R$ 0,00")
        self.configure(border_color="#E2E8F0")


class MetricsGridFrame(ctk.CTkFrame):
    """Container dos 2 cartões de métricas com linha e conector visual (✓ ou ✕)."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure((0, 1), weight=1, uniform="metric_card")

        self.canvas = ctk.CTkCanvas(self, bg="#F8FAFC", highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.card_xml = MetricCard(self, title="Documentos XML (NF-e / NFC-e)")
        self.card_xml.grid(row=0, column=0, padx=(0, 20), sticky="ew")

        self.card_fiscal = MetricCard(self, title="Arquivo Fiscal (SPED)")
        self.card_fiscal.grid(row=0, column=1, padx=(20, 0), sticky="ew")

        self.bind("<Configure>", lambda event: self._draw_connection())
        self.raw_metrics = {}

    def update_metrics(self, metrics: dict):
        self.raw_metrics = metrics

        xml_data = metrics.get("xmls", {"qty": 0, "val": 0})
        fiscal_data = metrics.get("fiscal_archives", {"qty": 0, "val": 0})

        xml_qty = xml_data.get("qty", 0)
        xml_val = xml_data.get("val", 0)
        fiscal_qty = fiscal_data.get("qty", 0)
        fiscal_val = fiscal_data.get("val", 0)

        self.card_xml.update_data(xml_qty, xml_val)
        self.card_fiscal.update_data(fiscal_qty, fiscal_val)

        is_qty_match = (xml_qty == fiscal_qty)
        is_val_match = (xml_val == fiscal_val)
        has_data = (xml_qty > 0 or fiscal_qty > 0)

        full_match = is_qty_match and is_val_match and has_data

        status = "MATCH" if full_match else ("MISMATCH" if has_data else "NEUTRAL")
        self.card_xml.set_border_status(status)
        self.card_fiscal.set_border_status(status)

        self.update_idletasks()
        self._draw_connection()

    def _draw_connection(self):
        self.canvas.delete("all")

        if not self.raw_metrics:
            return

        xml_data = self.raw_metrics.get("xmls", {"qty": 0, "val": 0})
        fiscal_data = self.raw_metrics.get("fiscal_archives", {"qty": 0, "val": 0})

        is_match = (
            xml_data.get("qty", 0) == fiscal_data.get("qty", 0) and
            xml_data.get("val", 0) == fiscal_data.get("val", 0) and
            xml_data.get("qty", 0) > 0
        )

        x1 = self.card_xml.winfo_x() + self.card_xml.winfo_width()
        y1 = self.card_xml.winfo_y() + (self.card_xml.winfo_height() // 2)

        x2 = self.card_fiscal.winfo_x()
        y2 = self.card_fiscal.winfo_y() + (self.card_fiscal.winfo_height() // 2)

        if x1 <= 0 or x2 <= 0:
            return

        color = "#10B981" if is_match else "#EF4444"
        icon_text = "✓" if is_match else "✕"

        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3, capstyle="round")

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        radius = 12

        self.canvas.create_oval(
            mid_x - radius, mid_y - radius,
            mid_x + radius, mid_y + radius,
            fill=color, outline="#FFFFFF", width=2
        )

        self.canvas.create_text(
            mid_x, mid_y,
            text=icon_text, fill="#FFFFFF",
            font=("Inter", 11, "bold")
        )

    def set_mode(self, is_sped: bool):
        fiscal_title = "Arquivo Fiscal (SPED)" if is_sped else "Arquivo Fiscal (Sintegra)"
        self.card_fiscal.set_title(fiscal_title)

    def reset(self):
        self.raw_metrics = {}
        self.canvas.delete("all")
        self.card_xml.reset()
        self.card_fiscal.reset()