import sys
import ctypes
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from src.views.components.header import HeaderFrame
from src.views.components.file_card import FileSelectionCard
from src.app_paths import PATHS
from src.services.audit_service import AuditService

ctk.set_appearance_mode("Light")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._set_windows_app_id()

        self.title("TRM Análises - Auditoria Fiscal")
        self.geometry("980x620")
        self.minsize(900, 580)
        self.configure(fg_color="#F8FAFC")

        self._set_app_icon()
        self._build_widgets()

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
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.iconphoto(False, photo)
        else:
            print(f"Aviso: Ícone não encontrado em {icon_path}")

    def _build_widgets(self):
        self.header = HeaderFrame(self)
        self.header.pack(fill="x", padx=30, pady=(24, 20))

        self.divider = ctk.CTkFrame(self, height=1, fg_color="#E2E8F0")
        self.divider.pack(fill="x", padx=30, pady=(0, 24))

        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=30)

        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="card")
        self.grid_container.grid_rowconfigure((0, 1), weight=0)

        self.card_nfce = FileSelectionCard(self.grid_container, title="NFC-e (XMLs)", is_directory=True)
        self.card_nfce.grid(row=0, column=0, padx=(0, 10), pady=(0, 20), sticky="ew")

        self.card_nfe = FileSelectionCard(self.grid_container, title="NF-e (XMLs)", is_directory=True)
        self.card_nfe.grid(row=0, column=1, padx=(10, 0), pady=(0, 20), sticky="ew")

        self.card_sped_fiscal = FileSelectionCard(self.grid_container, title="SPED Fiscal (.txt)", is_directory=False)
        self.card_sped_fiscal.grid(row=1, column=0, padx=(0, 10), pady=0, sticky="ew")

        self.card_sped_cofins = FileSelectionCard(self.grid_container, title="SPED Contribuições (.txt)", is_directory=False)
        self.card_sped_cofins.grid(row=1, column=1, padx=(10, 0), pady=0, sticky="ew")

        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=30, pady=30)

        self.btn_execute = ctk.CTkButton(
            self.footer_frame,
            text="▶   Executar Auditoria",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            fg_color="#0F172A",
            hover_color="#1E293B",
            text_color="#FFFFFF",
            corner_radius=8,
            height=46,
            command=self.run_audit
        )
        self.btn_execute.pack(fill="x", ipady=2)

    def run_audit(self):
        xml_dir_raw = self.card_nfe.get_path() or self.card_nfce.get_path()
        sped_file_raw = self.card_sped_cofins.get_path() or self.card_sped_fiscal.get_path()

        if not xml_dir_raw:
            messagebox.showwarning("Aviso", "Por favor, selecione ao menos um diretório de XMLs (NF-e ou NFC-e).")
            return

        if not sped_file_raw:
            messagebox.showwarning("Aviso", "Por favor, selecione ao menos um arquivo SPED (.txt).")
            return

        xml_dir = Path(xml_dir_raw)
        sped_path = Path(sped_file_raw)

        if not xml_dir.exists():
            messagebox.showerror("Erro", f"O diretório de XMLs informado não existe:\n{xml_dir}")
            return

        if not sped_path.exists():
            messagebox.showerror("Erro", f"O arquivo SPED informado não existe:\n{sped_path}")
            return

        self.btn_execute.configure(state="disabled", text="⏳ Processando Auditoria...")
        self.update_idletasks()

        try:
            audit_service = AuditService(xml_dir=xml_dir, sped_path=sped_path)

            audit_service.run_pipeline()

            messagebox.showinfo(
                "Sucesso", 
                f"Auditoria concluída com sucesso!\n\nRelatório gerado em:\n{PATHS.outputs_dir.resolve()}"
            )

        except Exception as e:
            messagebox.showerror("Erro na Auditoria", f"Ocorreu um erro durante a execução:\n{e}")

        finally:
            self.btn_execute.configure(state="normal", text="▶   Executar Auditoria")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()