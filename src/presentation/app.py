import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Correção dos caminhos de importação incluindo a raiz 'src'
from src.services.get_xml import get_xml_files_from_directory
from src.services.process_xml_files import process_xml_files
from src.parsers.sped_parser import parse_sped
from src.services.process_sped import process_sped_file
from src.services.audit import audit_query

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AuditApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Automação de Auditoria Fiscal")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.configure(fg_color="#F4F6F9")

        self.paths = {
            "XMLs": None,
            "SPED Cofins": None,
            "SPED IPI": None
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="")

        self._build_header()
        self._build_cards()
        self._build_action_button()

    def _build_header(self):
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Automação de Comparação de Arquivos",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color="#1E293B"
        )
        self.title_label.pack(pady=(0, 30))

    def _build_cards(self):
        self.cards_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.cards_frame.pack(pady=(0, 40))

        self.card_configs = [
            {"key": "XMLs", "label": "Selecione a Pasta 1\n(Diretório XMLs)"},
            {"key": "SPED Cofins", "label": "Selecione o Arquivo 2\n(SPED Cofins)"},
            {"key": "SPED IPI", "label": "Selecione o Arquivo 3\n(SPED IPI)"}
        ]

        self.card_widgets = {}

        for index, item in enumerate(self.card_configs):
            key = item["key"]
            
            card = ctk.CTkFrame(
                self.cards_frame, width=200, height=200, corner_radius=12,
                fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0", cursor="hand2"
            )
            card.pack_propagate(False)
            card.grid(row=0, column=index, padx=15)

            icon_label = ctk.CTkLabel(
                card, text="📁" if key == "XMLs" else "📄", 
                font=ctk.CTkFont(size=42), text_color="#64748B"
            )
            icon_label.pack(expand=True, pady=(20, 0))

            text_label = ctk.CTkLabel(
                card, text=item["label"], font=ctk.CTkFont(family="Helvetica", size=13),
                text_color="#64748B", justify="center"
            )
            text_label.pack(expand=True, pady=(0, 20))

            for widget in (card, icon_label, text_label):
                widget.bind("<Button-1>", lambda event, k=key: self.select_path(k))

            self.card_widgets[key] = {
                "card": card, "icon": icon_label, "label": text_label
            }

    def _build_action_button(self):
        self.btn_compare = ctk.CTkButton(
            self.main_container,
            text="Comparar Arquivos",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            corner_radius=8,
            width=220,
            height=45,
            command=self.run_audit
        )
        self.btn_compare.pack()

    def select_path(self, key):
        if key == "XMLs":
            path_selected = filedialog.askdirectory(title=f"Selecione a pasta de {key}")
        else:
            path_selected = filedialog.askopenfilename(
                title=f"Selecione o arquivo {key}",
                filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
            )
        
        if path_selected:
            self.paths[key] = path_selected
            item_name = os.path.basename(path_selected) or path_selected
            
            widgets = self.card_widgets[key]
            widgets["card"].configure(fg_color="#EFF6FF", border_color="#3B82F6")
            widgets["icon"].configure(text="✅", text_color="#3B82F6")
            
            icon_prefix = "📂" if key == "XMLs" else "📄"
            widgets["label"].configure(
                text=f"{key}\n\n{icon_prefix} {item_name[:15]}...", 
                text_color="#1E3A8A"
            )

    def run_audit(self):
        missing = [k for k, v in self.paths.items() if v is None]
        if missing:
            messagebox.showwarning("Atenção", f"Falta selecionar: {', '.join(missing)}")
            return

        try:
            self.btn_compare.configure(state="disabled", text="Processando...")
            self.update()

            # 1. Leitura e processamento de XMLs
            xml_files = get_xml_files_from_directory(self.paths["XMLs"])
            process_xml_files(xml_files)

            # 2. Parsing e processamento do SPED COFINS
            sped_cofins_data = parse_sped(self.paths["SPED Cofins"])
            process_sped_file(sped_cofins_data, "COFINS")

            # 3. Parsing e processamento do SPED IPI
            sped_ipi_data = parse_sped(self.paths["SPED IPI"])
            process_sped_file(sped_ipi_data, "ICMS")

            # 4. Execução da Query de Auditoria
            df = audit_query()

            # 5. Exportação dos Resultados
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Arquivo CSV", "*.csv"), ("Excel", "*.xlsx")],
                title="Salvar Resultado da Auditoria"
            )

            if output_file:
                if output_file.endswith('.csv'):
                    df.to_csv(output_file, index=False)
                else:
                    df.to_excel(output_file, index=False)
                    
                messagebox.showinfo("Sucesso", f"Auditoria finalizada!\nResultado salvo em:\n{output_file}")
            else:
                messagebox.showinfo("Aviso", "A auditoria foi concluída, mas o arquivo de resultados não foi salvo.")

        except Exception as e:
            messagebox.showerror("Erro de Processamento", f"Ocorreu um erro durante a auditoria:\n\n{str(e)}")
        finally:
            self.btn_compare.configure(state="normal", text="Comparar Arquivos")

if __name__ == "__main__":
    app = AuditApp()
    app.mainloop()