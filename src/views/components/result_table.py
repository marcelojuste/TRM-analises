import os
import subprocess
import sys
from pathlib import Path
from tkinter import ttk, messagebox
import customtkinter as ctk


class ResultsTableFrame(ctk.CTkFrame):
    def __init__(self, master, open_excel_callback=None, **kwargs):
        super().__init__(
            master,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
            **kwargs
        )

        self.excel_path = None
        self.open_excel_callback = open_excel_callback

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_container = ctk.CTkFrame(self, fg_color="transparent")
        self.header_container.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="ew")
        self.header_container.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self.header_container,
            text="PRÉVIA DO RELATÓRIO GERADO",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, sticky="w")

        self.btn_open_excel = ctk.CTkButton(
            self.header_container,
            text="📊 Abrir Planilha Excel",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            height=28,
            corner_radius=6,
            command=self._on_open_excel_clicked
        )
        self.btn_open_excel.grid(row=0, column=1, sticky="e", padx=(10, 0))

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
            font=("Inter", 9)
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground="#475569",
            font=("Inter", 9, "bold"),
            relief="flat"
        )
        style.map("Treeview", background=[("selected", "#CBD5E1")], foreground=[("selected", "#0F172A")])

        self.tree = ttk.Treeview(self.table_container, show="headings", selectmode="browse")

        self.tree.tag_configure("XML_AUSENTE", background="#FEE2E2", foreground="#991B1B")
        self.tree.tag_configure("SPED_AUSENTE", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("DIVERGENCIA", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("OK", background="#DCFCE7", foreground="#166534")

        self.vsb = ctk.CTkScrollbar(self.table_container, orientation="vertical", command=self.tree.yview)
        self.hsb = ctk.CTkScrollbar(self.table_container, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(2, 0), pady=0)
        self.hsb.grid(row=1, column=0, sticky="ew", padx=0, pady=(2, 0))

    def set_title_info(self, company_name: str = None):
        if company_name and company_name.strip() and company_name.upper() != "EMPRESA_DESCONHECIDA":
            self.lbl_title.configure(text=f"PRÉVIA DO RELATÓRIO — {company_name.strip().upper()}")
        else:
            self.lbl_title.configure(text="PRÉVIA DO RELATÓRIO GERADO")

    def set_excel_path(self, excel_path):
        self.excel_path = excel_path

    def _on_open_excel_clicked(self):
        if self.open_excel_callback and callable(self.open_excel_callback):
            self.open_excel_callback(self.excel_path)
            return

        if not self.excel_path or not os.path.exists(str(self.excel_path)):
            messagebox.showerror("Erro", "O arquivo Excel da auditoria não foi encontrado.")
            return

        try:
            excel_str_path = str(Path(self.excel_path).resolve())
            if sys.platform.startswith("win"):
                os.startfile(excel_str_path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", excel_str_path], check=True)
            else:
                subprocess.run(["xdg-open", excel_str_path], check=True)
        except Exception as e:
            messagebox.showerror("Erro ao abrir planilha", f"Não foi possível abrir o arquivo Excel:\n{e}")

    def load_excel_data(self, columns: list, rows: list, company_name: str = None, excel_path=None):
        self.clear()

        if company_name:
            self.set_title_info(company_name)
        if excel_path:
            self.set_excel_path(excel_path)

        clean_columns = [f"col_{i}" for i in range(len(columns))]
        self.tree["columns"] = clean_columns

        status_col_idx = None
        for i, col_name in enumerate(columns):
            col_key = clean_columns[i]
            col_text = str(col_name) if col_name is not None else f"COLUNA {i+1}"

            anchor = "center" if "MODELO" in col_text.upper() or "STATUS" in col_text.upper() else "w"
            width = 100 if "MODELO" in col_text.upper() else 140

            self.tree.heading(col_key, text=col_text.strip().upper(), anchor=anchor)
            self.tree.column(col_key, width=width, minwidth=70, anchor=anchor)

            if col_text and "STATUS" in col_text.strip().upper():
                status_col_idx = i

        for row in rows:
            formatted_row = [str(val) if val is not None else "" for val in row]
            
            row_tag = ()
            if status_col_idx is not None and status_col_idx < len(formatted_row):
                status_val = formatted_row[status_col_idx].upper()
                if "XML_AUSENTE" in status_val:
                    row_tag = ("XML_AUSENTE",)
                elif "DIVERGENCIA" in status_val or "SPED_AUSENTE" in status_val:
                    row_tag = ("DIVERGENCIA",)
                elif "OK" in status_val:
                    row_tag = ("OK",)

            self.tree.insert("", "end", values=formatted_row, tags=row_tag)

    def clear(self):
        """Limpa todas as linhas e colunas existentes."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()