import tkinter as tk
from tkinter import ttk
import customtkinter as ctk


class ResultsTableFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E2E8F0",
            **kwargs
        )

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.lbl_title = ctk.CTkLabel(
            self,
            text="PRÉVIA DO RELATÓRIO GERADO",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="ew")

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

    def load_excel_data(self, columns: list, rows: list):
        """Limpa a tabela, insere as colunas e colore as linhas de acordo com o status."""
        self.clear()

        clean_columns = [f"col_{i}" for i in range(len(columns))]
        self.tree["columns"] = clean_columns

        status_col_idx = None
        for i, col_name in enumerate(columns):
            col_key = clean_columns[i]
            col_text = str(col_name) if col_name is not None else f"COLUNA {i+1}"
            self.tree.heading(col_key, text=col_text.strip().upper(), anchor="w")
            self.tree.column(col_key, width=140, minwidth=80, anchor="w")

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