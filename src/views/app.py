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
from src.views.components.file_card import FiscalFileSelectionCard, XMLSelectionCard
from src.views.components.header import HeaderFrame
from src.views.components.metric_card import MetricsGridFrame
from src.views.components.result_table import ResultsTableFrame

ctk.set_appearance_mode("Light")


class AnimatedModeSwitch(ctk.CTkFrame):
    """Container estilizado com Switch animado para alternar entre SINTEGRA e SPED."""

    def __init__(self, master, on_mode_changed=None, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            height=38,
            **kwargs
        )
        self.on_mode_changed = on_mode_changed
        self.is_sped = True  # Padrão: True = SPED, False = SINTEGRA

        self._build_switch()

    def _build_switch(self):
        self.bg_frame = ctk.CTkFrame(
            self,
            fg_color="#DBEAFE",  # Fundo inicial para modo SPED (Azul claro)
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

        # Switch customizado com animação nativa do CustomTkinter
        self.switch_control = ctk.CTkSwitch(
            self.bg_frame,
            text="",
            width=46,
            height=24,
            switch_width=44,
            switch_height=22,
            progress_color="#2563EB",  # Azul no SPED
            button_color="#FFFFFF",
            button_hover_color="#F8FAFC",
            command=self._on_switch_toggled
        )
        self.switch_control.pack(side="left", padx=2)
        self.switch_control.select()  # Ativado por padrão (SPED)

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
            # Modo SPED (Direita ativa em azul)
            self.bg_frame.configure(fg_color="#DBEAFE", border_color="#BFDBFE")
            self.switch_control.configure(progress_color="#2563EB")
            self.lbl_sped.configure(text_color="#1D4ED8")
            self.lbl_sintegra.configure(text_color="#94A3B8")
        else:
            # Modo SINTEGRA (Esquerda ativa em laranja)
            self.bg_frame.configure(fg_color="#FFEDD5", border_color="#FED7AA")
            self.switch_control.configure(progress_color="#EA580C")
            self.lbl_sintegra.configure(text_color="#C2410C")
            self.lbl_sped.configure(text_color="#94A3B8")

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.switch_control.configure(state=state)


class MainWindow(ctk.CTk):
    COLOR_PALETTES = {
        "SPED": {
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
        },
        "SINTEGRA": {
            "primary": "#EA580C",
            "primary_hover": "#C2410C",
        }
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

        # Seletor com Switch e cores dinamicas por modo
        self.mode_switch = AnimatedModeSwitch(
            self.top_control_container,
            on_mode_changed=self._on_mode_changed
        )
        self.mode_switch.pack(side="right")

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="x", padx=30, pady=(0, 12))
        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="card")

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
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self.footer_frame.grid_columnconfigure(1, weight=0)

        self.btn_execute = ctk.CTkButton(
            self.footer_frame,
            text="▶   Executar Auditoria",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#FFFFFF",
            corner_radius=8,
            height=44,
            command=self.run_audit
        )
        self.btn_execute.grid(row=0, column=0, sticky="ew")

        # Botão Vermelho de Cancelar/Reiniciar (oculto por padrão)
        self.btn_reset = ctk.CTkButton(
            self.footer_frame,
            text="🛑   Cancelar e Reiniciar",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            corner_radius=8,
            height=44,
            command=self.reset_app
        )

        self.results_table = ResultsTableFrame(self, export_excel_callback=self._export_to_excel_and_open)

    def _on_mode_changed(self, is_sped: bool):
        self.app_state.set_mode(is_sped)
        self._apply_theme_colors()

    def _apply_theme_colors(self):
        mode_key = "SPED" if self.app_state.is_sped_mode else "SINTEGRA"
        palette = self.COLOR_PALETTES[mode_key]

        self.btn_execute.configure(fg_color=palette["primary"], hover_color=palette["primary_hover"])

        self.card_fiscal.set_mode(self.app_state.is_sped_mode)
        self.metrics_grid.set_mode(self.app_state.is_sped_mode)
        self.header.update_mode_theme(self.app_state.is_sped_mode)

    def _set_ui_processing_state(self, is_processing: bool):
        self.app_state.is_running = is_processing
        enabled = not is_processing

        self.card_xmls.set_enabled(enabled)
        self.card_fiscal.set_enabled(enabled)
        self.mode_switch.set_enabled(enabled)
        self.results_table.set_enabled(enabled)

        palette = self.COLOR_PALETTES["SPED" if self.app_state.is_sped_mode else "SINTEGRA"]

        if is_processing:
            self.footer_frame.grid_columnconfigure(0, weight=3)
            self.footer_frame.grid_columnconfigure(1, weight=1)
            
            self.btn_execute.configure(state="disabled", text="⏳ Processando Auditoria...")
            self.btn_execute.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            self.btn_reset.grid(row=0, column=1, sticky="ew")
        else:
            self.btn_reset.grid_forget()
            self.footer_frame.grid_columnconfigure(0, weight=1)
            self.footer_frame.grid_columnconfigure(1, weight=0)
            
            self.btn_execute.configure(
                state="normal",
                text="▶   Executar Auditoria",
                fg_color=palette["primary"],
                hover_color=palette["primary_hover"]
            )
            self.btn_execute.grid(row=0, column=0, sticky="ew", padx=0)

    def run_audit(self):
        if not self.app_state.xml_paths:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um diretório contendo arquivos XML.")
            return

        if not self.app_state.fiscal_paths:
            messagebox.showwarning("Seleção Insuficiente", "Selecione ao menos um arquivo fiscal (.txt).")
            return

        self.cancel_event.clear()
        self._set_ui_processing_state(True)

        fiscal_1 = self.app_state.fiscal_paths[0] if len(self.app_state.fiscal_paths) > 0 else None
        fiscal_2 = self.app_state.fiscal_paths[1] if len(self.app_state.fiscal_paths) > 1 else None

        def worker():
            try:
                audit_service = AuditService(
                    fiscal_archive_path=fiscal_1,
                    fiscal_archive_path_2=fiscal_2,
                    nfe_dir_path=self.app_state.xml_paths[0] if len(self.app_state.xml_paths) > 0 else None,
                    nfce_dir_path=self.app_state.xml_paths[1] if len(self.app_state.xml_paths) > 1 else None,
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

    def _process_queue(self):
        try:
            while not self.msg_queue.empty():
                status, payload = self.msg_queue.get_nowait()

                if status == "SUCCESS":
                    self.app_state.enterprise_name = payload.get("enterprise", "EMPRESA_DESCONHECIDA")
                    self.app_state.metrics = payload.get("metrics", {})
                    self.app_state.audit_results = payload.get("audit_results", pd.DataFrame())

                    self.metrics_grid.update_metrics(self.app_state.metrics)
                    self.results_table.load_dataframe(
                        df_results=self.app_state.audit_results, company_name=self.app_state.enterprise_name
                    )
                    self.results_table.pack(fill="both", expand=True, padx=30, pady=(0, 20))
                    self._set_ui_processing_state(False)

                    messagebox.showinfo(
                        "Sucesso", "Auditoria concluída com sucesso!\n\nPrévia disponível abaixo."
                    )

                elif status == "CANCELLED":
                    self.reset_ui_and_state()
                    messagebox.showwarning("Cancelado", "A operação de auditoria foi cancelada e reiniciada.")

                elif status == "ERROR":
                    self._set_ui_processing_state(False)
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

    def reset_app(self):
        if self.app_state.is_running:
            self.cancel_event.set()
        else:
            self.reset_ui_and_state()

    def reset_ui_and_state(self):
        self.app_state.reset_paths_and_metrics()
        self.card_xmls.clear_selection()
        self.card_fiscal.clear_selection()
        self.metrics_grid.reset()
        self.results_table.clear()
        self.results_table.pack_forget()
        self._set_ui_processing_state(False)
        self.geometry("980x720")