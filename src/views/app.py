from pathlib import Path
import sys
import os
import threading
import queue
import subprocess
from tkinter import messagebox

import customtkinter as ctk
import pandas as pd
from PIL import Image, ImageTk

from src.path_manager import PATHS
from src.views.app_state import AppState
from src.services.audit_service import AuditService
from src.services.exporters.excel.excel_exporter import ExcelExport
from src.views.components.file_card.xml_card import XMLSelectionCard
from src.views.components.file_card.fiscal_card import FiscalFileSelectionCard
from src.views.components.mode_switch import AnimatedModeSwitch
from src.views.components.header import HeaderFrame
from src.views.components.metric_card import MetricsGridFrame
from src.views.components.result_table import ResultsTableFrame

ctk.set_appearance_mode("Light")


class MainWindow(ctk.CTk):
    COLOR_PALETTES = {
        "SPED": {"primary": "#2563EB", "primary_hover": "#1D4ED8"},
        "SINTEGRA": {"primary": "#EA580C", "primary_hover": "#C2410C"}
    }

    def __init__(self):
        super().__init__()

        self.app_state = AppState()
        self.msg_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.audit_thread = None

        self.title("TRM Análises - Auditoria Fiscal")
        self.geometry("980x720")
        self.minsize(900, 650)
        self.configure(fg_color="#F8FAFC")

        self._set_app_icon()
        self._build_widgets()
        self._apply_theme_colors()

        self.after(100, self._process_queue)

    def _set_app_icon(self):
        icon_path = PATHS.icons_dir / "iconTRM.ico"
        if icon_path.exists():
            abs_icon_path = str(icon_path.resolve())
            try:
                self.iconbitmap(abs_icon_path)
                img = Image.open(abs_icon_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(True, photo)
                self._app_icon = photo
            except Exception as e:
                print(f"Erro ao carregar ícone: {e}")

    def _build_widgets(self):
        self.header = HeaderFrame(self)
        self.header.pack(fill="x", padx=30, pady=(20, 10))

        self.divider = ctk.CTkFrame(self, height=1, fg_color="#E2E8F0")
        self.divider.pack(fill="x", padx=30, pady=(0, 10))

        self.top_control_container = ctk.CTkFrame(self, fg_color="transparent")
        self.top_control_container.pack(fill="x", padx=30, pady=(0, 10))

        self.mode_switch = AnimatedModeSwitch(
            self.top_control_container,
            on_mode_changed=self._on_mode_changed
        )
        self.mode_switch.pack(side="right")

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="x", padx=30, pady=(0, 12))
        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="card")
        self.grid_container.grid_rowconfigure(0, weight=1)

        self.card_xmls = XMLSelectionCard(
            self.grid_container,
            on_change=lambda paths: setattr(self.app_state, 'xml_paths', paths)
        )
        self.card_xmls.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.card_fiscal = FiscalFileSelectionCard(
            self.grid_container,
            is_sped=self.app_state.is_sped_mode,
            on_change=lambda paths: setattr(self.app_state, 'fiscal_paths', paths)
        )
        self.card_fiscal.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        self.metrics_grid = MetricsGridFrame(self)
        self.metrics_grid.pack(fill="x", padx=30, pady=(0, 12))

        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=30, pady=(0, 12))

        self.btn_execute = ctk.CTkButton(
            self.footer_frame,
            text="▶   Executar Auditoria",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#FFFFFF",
            corner_radius=8,
            height=44,
            command=self.run_audit
        )

        self.btn_cancel = ctk.CTkButton(
            self.footer_frame,
            text="🛑   Cancelar Operação",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            corner_radius=8,
            height=44,
            command=self.cancel_audit
        )

        self.btn_reset = ctk.CTkButton(
            self.footer_frame,
            text="🔄   Reiniciar Operação",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            corner_radius=8,
            height=44,
            command=self.reset_ui_and_state
        )

        self._update_footer_layout("IDLE")

        self.results_table = ResultsTableFrame(self, export_excel_callback=self._export_to_excel_and_open)

    def _update_footer_layout(self, state: str):
        self.btn_execute.grid_forget()
        self.btn_cancel.grid_forget()
        self.btn_reset.grid_forget()

        palette = self.COLOR_PALETTES["SPED" if self.app_state.is_sped_mode else "SINTEGRA"]

        if state == "RUNNING":
            self.footer_frame.grid_columnconfigure(0, weight=1, uniform="footer_btn")
            self.footer_frame.grid_columnconfigure(1, weight=1, uniform="footer_btn")

            self.btn_execute.configure(state="disabled", text="⏳ Processando Auditoria...", fg_color=palette["primary"])
            self.btn_execute.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            self.btn_cancel.configure(fg_color="#EF4444", hover_color="#DC2626")
            self.btn_cancel.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        elif state == "COMPLETED":
            self.footer_frame.grid_columnconfigure(0, weight=1, uniform="footer_btn")
            self.footer_frame.grid_columnconfigure(1, weight=1, uniform="footer_btn")

            self.btn_execute.configure(state="normal", text="▶   Executar Auditoria", fg_color=palette["primary"], hover_color=palette["primary_hover"])
            self.btn_execute.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            self.btn_reset.configure(fg_color="#EF4444", hover_color="#DC2626")
            self.btn_reset.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        else:
            self.footer_frame.grid_columnconfigure(0, weight=1, uniform="")
            self.footer_frame.grid_columnconfigure(1, weight=0, uniform="")

            self.btn_execute.configure(state="normal", text="▶   Executar Auditoria", fg_color=palette["primary"], hover_color=palette["primary_hover"])
            self.btn_execute.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0)

    def _on_mode_changed(self, is_sped: bool):
        self.app_state.set_mode(is_sped)
        self._apply_theme_colors()

    def _apply_theme_colors(self):
        mode_key = "SPED" if self.app_state.is_sped_mode else "SINTEGRA"
        palette = self.COLOR_PALETTES[mode_key]

        self.btn_execute.configure(fg_color=palette["primary"], hover_color=palette["primary_hover"])
        self.btn_cancel.configure(fg_color="#EF4444", hover_color="#DC2626")
        self.btn_reset.configure(fg_color="#EF4444", hover_color="#DC2626")

        self.card_fiscal.set_mode(self.app_state.is_sped_mode)
        self.metrics_grid.set_mode(self.app_state.is_sped_mode)
        self.header.update_mode_theme(self.app_state.is_sped_mode)

    def run_audit(self):
        if not self.app_state.xml_paths:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um diretório contendo arquivos XML.")
            return

        if not self.app_state.fiscal_paths:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um arquivo fiscal (.txt).")
            return

        self.cancel_event.clear()
        self.app_state.is_running = True

        self.card_xmls.set_enabled(False)
        self.card_fiscal.set_enabled(False)
        self.mode_switch.set_enabled(False)

        self._update_footer_layout("RUNNING")

        fiscal_1 = self.app_state.fiscal_paths[0] if len(self.app_state.fiscal_paths) > 0 else None
        fiscal_2 = self.app_state.fiscal_paths[1] if len(self.app_state.fiscal_paths) > 1 else None

        xml_1 = self.app_state.xml_paths[0] if len(self.app_state.xml_paths) > 0 else None
        xml_2 = self.app_state.xml_paths[1] if len(self.app_state.xml_paths) > 1 else None

        def worker():
            try:
                audit_service = AuditService(
                    fiscal_archive_path=fiscal_1,
                    fiscal_archive_path_2=fiscal_2,
                    nfe_dir_path=xml_1,
                    nfce_dir_path=xml_2,
                    cancel_event=self.cancel_event,
                    is_sped=self.app_state.is_sped_mode
                )

                audit_output = audit_service.run_pipeline()

                if self.cancel_event.is_set():
                    self.msg_queue.put(("CANCELLED", None))
                else:
                    self.msg_queue.put(("SUCCESS", audit_output))

            except InterruptedError:
                self.msg_queue.put(("CANCELLED", None))
            except Exception as e:
                if self.cancel_event.is_set():
                    self.msg_queue.put(("CANCELLED", None))
                else:
                    self.msg_queue.put(("ERROR", str(e)))

        self.audit_thread = threading.Thread(target=worker, daemon=True)
        self.audit_thread.start()

    def cancel_audit(self):
        if self.app_state.is_running:
            self.cancel_event.set()

    def _process_queue(self):
        try:
            while not self.msg_queue.empty():
                status, payload = self.msg_queue.get_nowait()
                self.app_state.is_running = False

                self.card_xmls.set_enabled(True)
                self.card_fiscal.set_enabled(True)
                self.mode_switch.set_enabled(True)

                if status == "SUCCESS":
                    self.app_state.enterprise_name = payload.get("enterprise", "EMPRESA_DESCONHECIDA")
                    self.app_state.metrics = payload.get("metrics", {})
                    self.app_state.audit_results = payload.get("audit_results", pd.DataFrame())

                    self.metrics_grid.update_metrics(self.app_state.metrics)
                    self.results_table.load_dataframe(
                        df_results=self.app_state.audit_results, company_name=self.app_state.enterprise_name
                    )
                    self.results_table.pack(fill="both", expand=True, padx=30, pady=(0, 20))

                    self._update_footer_layout("COMPLETED")
                    messagebox.showinfo("Sucesso", "Auditoria concluída com sucesso!\n\nPrévia disponível abaixo.")

                elif status == "CANCELLED":
                    self.reset_ui_and_state()
                    messagebox.showwarning("Cancelado", "A operação de auditoria foi cancelada e reiniciada.")

                elif status == "ERROR":
                    self._update_footer_layout("COMPLETED")
                    messagebox.showerror("Erro na Auditoria", f"Ocorreu um erro durante a execução:\n\n{payload}")

        finally:
            self.after(100, self._process_queue)

    def _export_to_excel_and_open(self, df_results: pd.DataFrame):
        if df_results is None or df_results.empty:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")
            return

        try:
            output_file = PATHS.outputs_dir / f"relatorio_auditoria_{self.app_state.enterprise_name}.xlsx"
            exporter = ExcelExport(output_xlsx_path=output_file, enterprise_name=self.app_state.enterprise_name)
            exporter.export_dataframe_to_excel(df_results)

            excel_str_path = str(output_file.resolve())
            if sys.platform.startswith("win"):
                os.startfile(excel_str_path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", excel_str_path], check=True)
            else:
                subprocess.run(["xdg-open", excel_str_path], check=True)

        except Exception as e:
            messagebox.showerror("Erro ao Gerar Excel", f"Falha ao exportar:\n\n{e}")

    def reset_ui_and_state(self):
        self.app_state.reset_paths_and_metrics()
        self.card_xmls.clear_selection()
        self.card_fiscal.clear_selection()
        self.metrics_grid.reset()
        self.results_table.clear()
        self.results_table.pack_forget()

        self.card_xmls.set_enabled(True)
        self.card_fiscal.set_enabled(True)
        self.mode_switch.set_enabled(True)

        self._update_footer_layout("IDLE")
        self.geometry("980x720")