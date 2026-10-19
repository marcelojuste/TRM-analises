import ctypes
from pathlib import Path
import sys
import os
import threading
from tkinter import messagebox
import subprocess

import customtkinter as ctk
import pandas as pd
from PIL import Image, ImageTk

from src.path_manager import PATHS
from src.services.audit_service import AuditService
from src.services.exporters.excel.excel_exporter import ExcelExport
from src.views.components.file_card import FiscalFileSelectionCard, XMLSelectionCard
from src.views.components.header import HeaderFrame
from src.views.components.metric_card import MetricsGridFrame
from src.views.components.result_table import ResultsTableFrame

ctk.set_appearance_mode("Light")


class MainWindow(ctk.CTk):
    COLOR_PALETTES = {
        "SPED": {
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "switch_progress": "#3B82F6",
        },
        "SINTEGRA": {
            "primary": "#EA580C",
            "primary_hover": "#C2410C",
            "switch_progress": "#F97316",
        }
    }

    def __init__(self):
        super().__init__()

        self._set_windows_app_id()

        self.title("TRM Análises - Auditoria Fiscal")
        self.geometry("980x720")
        self.minsize(900, 650)
        self.configure(fg_color="#F8FAFC")

        self.is_running = False
        self.cancel_event = threading.Event()
        self.audit_thread = None
        self.is_sped_mode = True
        self.last_enterprise_name = "EMPRESA_DESCONHECIDA"

        self._set_app_icon()
        self._build_widgets()
        self._apply_theme_colors()

    def _set_windows_app_id(self):
        if sys.platform.startswith("win"):
            my_app_id = "trmsistemas.trmanalises.auditor.1.0"
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
            except Exception as e:
                print(f"Erro ao definir AppUserModelID: {e}")

    def _set_app_icon(self):
        icon_path = PATHS.icons_dir / "iconTRM.ico"
        if icon_path.exists():
            abs_icon_path = str(icon_path.resolve())
            try:
                self.iconbitmap(abs_icon_path)
            except Exception as e:
                print(f"Erro no iconbitmap: {e}")

            try:
                img = Image.open(abs_icon_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(True, photo)
                self._app_icon = photo
            except Exception as e:
                print(f"Erro no iconphoto: {e}")

    def _build_widgets(self):
        self.header = HeaderFrame(self)
        self.header.pack(fill="x", padx=30, pady=(20, 10))

        self.divider = ctk.CTkFrame(self, height=1, fg_color="#E2E8F0")
        self.divider.pack(fill="x", padx=30, pady=(0, 10))

        self.top_control_container = ctk.CTkFrame(self, fg_color="transparent")
        self.top_control_container.pack(fill="x", padx=30, pady=(0, 10))

        self.mode_switch = ctk.CTkSwitch(
            self.top_control_container,
            text="Modo: SPED (Azul)",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#0F172A",
            command=self._on_switch_mode_toggled,
            progress_color="#3B82F6",
            button_color="#0F172A",
            button_hover_color="#1E293B",
        )
        self.mode_switch.pack(side="right")
        self.mode_switch.select()

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="x", padx=30, pady=(0, 12))
        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="card")

        self.card_xmls = XMLSelectionCard(self.grid_container)
        self.card_xmls.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.card_fiscal = FiscalFileSelectionCard(self.grid_container, is_sped=True)
        self.card_fiscal.grid(row=0, column=1, padx=(10, 0), sticky="ew")

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
        self.btn_execute.pack(fill="x", ipady=2)

        self.btn_clear = ctk.CTkButton(
            self.footer_frame,
            text="🔄   Limpar",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            fg_color="#FEE2E2",
            hover_color="#FCA5A5",
            text_color="#991B1B",
            corner_radius=8,
            height=44,
            command=self._on_clear_or_cancel_clicked
        )

        self.results_table = ResultsTableFrame(self, export_excel_callback=self._export_to_excel_and_open)

    def _on_switch_mode_toggled(self):
        self.is_sped_mode = bool(self.mode_switch.get())
        self._apply_theme_colors()

    def _apply_theme_colors(self):
        mode_key = "SPED" if self.is_sped_mode else "SINTEGRA"
        palette = self.COLOR_PALETTES[mode_key]

        switch_text = "Modo: SPED (Azul)" if self.is_sped_mode else "Modo: SINTEGRA (Laranja)"
        self.mode_switch.configure(
            text=switch_text,
            progress_color=palette["switch_progress"]
        )

        self.btn_execute.configure(
            fg_color=palette["primary"],
            hover_color=palette["primary_hover"]
        )

        self.card_fiscal.set_mode(self.is_sped_mode)
        self.metrics_grid.set_mode(self.is_sped_mode)
        self.header.update_mode_theme(self.is_sped_mode)

    def _set_ui_processing_state(self, is_processing: bool):
        self.is_running = is_processing
        enabled = not is_processing

        self.card_xmls.set_enabled(enabled)
        self.card_fiscal.set_enabled(enabled)
        self.mode_switch.configure(state="normal" if enabled else "disabled")
        self.results_table.set_enabled(enabled)

        palette = self.COLOR_PALETTES["SPED" if self.is_sped_mode else "SINTEGRA"]

        if is_processing:
            self.btn_execute.configure(state="disabled", text="⏳ Processando Auditoria...")
            self.btn_clear.configure(
                text="🛑   Cancelar Operação",
                fg_color="#EF4444",
                hover_color="#DC2626",
                text_color="#FFFFFF",
                state="normal"
            )
        else:
            self.btn_execute.configure(
                state="normal",
                text="▶   Executar Auditoria",
                fg_color=palette["primary"],
                hover_color=palette["primary_hover"]
            )
            self.btn_clear.configure(
                text="🔄   Limpar",
                fg_color="#FEE2E2",
                hover_color="#FCA5A5",
                text_color="#991B1B",
                state="normal"
            )

    def _on_clear_or_cancel_clicked(self):
        if self.is_running:
            self.cancel_event.set()
        else:
            self.reset_app()

    def _export_to_excel_and_open(self, df_results: pd.DataFrame):
        if df_results is None or df_results.empty:
            messagebox.showwarning("Aviso", "Não há dados no relatório para exportar.")
            return

        try:
            output_file = PATHS.outputs_dir / f"relatorio_auditoria_{self.last_enterprise_name}.xlsx"
            
            exporter = ExcelExport(output_xlsx_path=output_file, enterprise_name=self.last_enterprise_name)
            exporter.export_dataframe_to_excel(df_results)

            excel_str_path = str(output_file.resolve())
            if sys.platform.startswith("win"):
                os.startfile(excel_str_path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", excel_str_path], check=True)
            else:
                subprocess.run(["xdg-open", excel_str_path], check=True)

        except Exception as e:
            messagebox.showerror("Erro ao Gerar Excel", f"Falha ao exportar a planilha:\n\n{e}")

    def run_audit(self):
        xml_dirs = self.card_xmls.get_paths()
        fiscal_files = self.card_fiscal.get_paths()

        if not xml_dirs:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um diretório contendo arquivos XML.")
            return

        if not fiscal_files:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um arquivo fiscal (.txt).")
            return

        fiscal_1 = fiscal_files[0] if len(fiscal_files) > 0 else None
        fiscal_2 = fiscal_files[1] if len(fiscal_files) > 1 else None

        self.cancel_event.clear()
        self._set_ui_processing_state(True)
        self.update_idletasks()

        def worker():
            cancelled = False
            try:
                audit_service = AuditService(
                    fiscal_archive_path=fiscal_1,
                    fiscal_archive_path_2=fiscal_2,
                    nfe_dir_path=xml_dirs[0] if len(xml_dirs) > 0 else None,
                    nfce_dir_path=xml_dirs[1] if len(xml_dirs) > 1 else None,
                    cancel_event=self.cancel_event,
                    is_sped=self.is_sped_mode
                )

                audit_output = audit_service.run_pipeline()

                if self.cancel_event.is_set():
                    cancelled = True
                else:
                    self.last_enterprise_name = audit_output.get("enterprise", "EMPRESA_DESCONHECIDA")
                    metrics = audit_output.get("metrics", {})
                    audit_df = audit_output.get("audit_results", pd.DataFrame())

                    self.after(0, lambda: self.metrics_grid.update_metrics(metrics))

                    self.after(0, lambda: self.results_table.load_dataframe(
                        df_results=audit_df, company_name=self.last_enterprise_name
                    ))
                    self.after(0, lambda: self.results_table.pack(fill="both", expand=True, padx=30, pady=(0, 20)))

                    self.after(0, lambda: messagebox.showinfo(
                        "Sucesso", "Auditoria concluída com sucesso!\n\nVocê já pode visualizar a prévia na tabela ou exportar a planilha para Excel."
                    ))

            except InterruptedError:
                cancelled = True
            except Exception as e:
                if self.cancel_event.is_set():
                    cancelled = True
                else:
                    error_msg = str(e)
                    self.after(0, lambda msg=error_msg: messagebox.showerror("Erro na Auditoria", f"Ocorreu um erro durante a execução:\n\n{msg}"))
            finally:
                if cancelled or self.cancel_event.is_set():
                    self.after(0, self.reset_app)
                    self.after(0, lambda: messagebox.showwarning("Cancelado", "A operação de auditoria foi cancelada pelo usuário."))
                else:
                    self.after(0, lambda: self._set_ui_processing_state(False))

        self.audit_thread = threading.Thread(target=worker, daemon=True)
        self.audit_thread.start()

    def reset_app(self):
        self.card_xmls.clear_selection()
        self.card_fiscal.clear_selection()
        self.metrics_grid.reset()

        self.results_table.clear()
        self.results_table.pack_forget()

        self._set_ui_processing_state(False)
        self.geometry("980x720")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()