import os
from pathlib import Path
import subprocess
import sys
from tkinter import messagebox, ttk
import customtkinter as ctk
import pandas as pd


class ResultsTableFrame(ctk.CTkFrame):
    def __init__(self, master, export_excel_callback=None, **kwargs):
        super().__init__(
            master,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
            **kwargs
        )

        self.df_results: pd.DataFrame | None = None
        self.export_excel_callback = export_excel_callback

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_container = ctk.CTkFrame(self, fg_color="transparent")
        self.header_container.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="ew")
        self.header_container.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self.header_container,
            text="PRÉVIA DO RELATÓRIO GERADO",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, sticky="w")

        self.btn_export_excel = ctk.CTkButton(
            self.header_container,
            text="📊 Exportar para Excel",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=28,
            corner_radius=6,
            command=self._on_export_excel_clicked
        )
        self.btn_export_excel.grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#0F172A",
            rowheight=26,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 9)
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground="#475569",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        style.map("Treeview", background=[("selected", "#CBD5E1")], foreground=[("selected", "#0F172A")])

        self.tree = ttk.Treeview(self.table_container, show="headings", selectmode="browse")

        self.tree.tag_configure("CRITICAL", background="#FEE2E2", foreground="#991B1B")
        self.tree.tag_configure("WARNING", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("OK", background="#DCFCE7", foreground="#166534")

        self.vsb = ctk.CTkScrollbar(self.table_container, orientation="vertical", command=self.tree.yview)
        self.hsb = ctk.CTkScrollbar(self.table_container, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(2, 0), pady=0)
        self.hsb.grid(row=1, column=0, sticky="ew", padx=0, pady=(2, 0))

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_export_excel.configure(state=state)

    def set_title_info(self, company_name: str = None):
        if company_name and company_name.strip() and company_name.upper() != "EMPRESA_DESCONHECIDA":
            self.lbl_title.configure(text=f"PRÉVIA DO RELATÓRIO — {company_name.strip().upper()}")
        else:
            self.lbl_title.configure(text="PRÉVIA DO RELATÓRIO GERADO")

    def load_dataframe(self, df_results: pd.DataFrame, company_name: str = None):
        self.clear()
        self.df_results = df_results

        if company_name:
            self.set_title_info(company_name)

        if df_results is None or df_results.empty:
            return

        columns = list(df_results.columns)
        clean_columns = [f"col_{i}" for i in range(len(columns))]
        self.tree["columns"] = clean_columns

        status_col_idx = None
        for i, col_name in enumerate(columns):
            col_key = clean_columns[i]
            col_text = str(col_name).replace("_cents", "").replace("_val", "").replace("_", " ").upper()

            anchor = "center" if "MODEL" in col_text or "STATUS" in col_text else "w"
            width = 110 if "MODEL" in col_text else 140

            self.tree.heading(col_key, text=col_text.strip(), anchor=anchor)
            self.tree.column(col_key, width=width, minwidth=70, anchor=anchor)

            if "STATUS" in col_text:
                status_col_idx = i

        for row_tuple in df_results.itertuples(index=False):
            formatted_row = []
            for col_idx, val in enumerate(row_tuple):
                col_name = columns[col_idx].lower()
                if pd.isna(val) or val is None:
                    formatted_row.append("")
                elif ("cents" in col_name or "centavos" in col_name) and isinstance(val, (int, float)):
                    formatted_row.append(f"R$ {val / 100.0:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                else:
                    formatted_row.append(str(val))

            row_tag = ()
            if status_col_idx is not None and status_col_idx < len(formatted_row):
                status_val = formatted_row[status_col_idx].upper()
                if any(k in status_val for k in ["MISSING", "AUSENTE"]):
                    row_tag = ("CRITICAL",)
                elif any(k in status_val for k in ["DIVERGENCE", "DIVERGENCIA"]):
                    row_tag = ("WARNING",)
                elif "OK" in status_val:
                    row_tag = ("OK",)

            self.tree.insert("", "end", values=formatted_row, tags=row_tag)

    def _on_export_excel_clicked(self):
        if self.export_excel_callback and callable(self.export_excel_callback):
            self.export_excel_callback(self.df_results)

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
        self.df_results = None
        self.set_title_info(None)