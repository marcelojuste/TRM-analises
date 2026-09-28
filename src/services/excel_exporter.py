from pathlib import Path
import duckdb
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


class ExportService:
    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        sql_file_path: Path,
        output_xlsx_path: Path,
        enterprise_name: str = "EMPRESA_DESCONHECIDA"
    ):
        self.conn = conn
        self.sql_file_path = sql_file_path
        self.output_xlsx_path = output_xlsx_path
        self.enterprise_name = enterprise_name or "EMPRESA_DESCONHECIDA"

    def _get_status_style(self, status: str) -> tuple[PatternFill | None, Font | None]:
        """Aplica os mesmos tons e badges do aplicativo TRM Análises."""
        if status == "XML_AUSENTE":
            fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
            font = Font(name="Inter", size=10, bold=True, color="B91C1C")
            return fill, font

        if status in ("SPED_AUSENTE", "DIVERGENCIA_VALOR", "DIVERGENCIA_STATUS", "DIVERGENCIA_DATA"):
            fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
            font = Font(name="Inter", size=10, bold=True, color="B45309")
            return fill, font

        if status == "OK":
            fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
            font = Font(name="Inter", size=10, bold=True, color="15803D")
            return fill, font

        return None, None

    def export_query_to_excel(self) -> None:
        if not self.sql_file_path.exists():
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {self.sql_file_path}")

        sql_query = self.sql_file_path.read_text(encoding="utf-8").strip()
        self.output_xlsx_path.parent.mkdir(parents=True, exist_ok=True)

        cursor = self.conn.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]

        status_col_idx = columns.index("status_auditoria") if "status_auditoria" in columns else None

        wb = Workbook()
        ws = wb.active
        ws.title = "Auditoria Fiscal"
        ws.views.sheetView[0].showGridLines = True

        total_cols = len(columns)
        last_col_letter = get_column_letter(total_cols)

        full_border = Border(
            left=Side(style="thin", color="E2E8F0"),
            right=Side(style="thin", color="E2E8F0"),
            top=Side(style="thin", color="E2E8F0"),
            bottom=Side(style="thin", color="E2E8F0")
        )

        ws.merge_cells(f"A1:{last_col_letter}1")
        title_cell = ws["A1"]
        title_cell.value = "TRM Análises — RELATÓRIO DE AUDITORIA FISCAL"
        title_cell.font = Font(name="Inter", size=13, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        title_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 36

        ws.merge_cells(f"A2:{last_col_letter}2")
        subtitle_cell = ws["A2"]
        subtitle_cell.value = f"EMPRESA AUDITADA: {self.enterprise_name.upper()}"
        subtitle_cell.font = Font(name="Inter", size=10, bold=True, color="2563EB")
        subtitle_cell.fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        subtitle_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[2].height = 24

        header_font = Font(name="Inter", size=10, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        
        for col_idx, col_name in enumerate(columns, start=1):
            display_name = col_name.replace("_centavos", "").replace("_", " ").upper()
            
            cell = ws.cell(row=3, column=col_idx, value=display_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = full_border
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws.row_dimensions[3].height = 28

        base_font = Font(name="Inter", size=10, color="0F172A")

        align_left = Alignment(horizontal="left", vertical="center")
        align_center = Alignment(horizontal="center", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        current_row = 4
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break

            for row in rows:
                status_val = str(row[status_col_idx]) if status_col_idx is not None else ""
                row_fill, row_font = self._get_status_style(status_val)

                ws.row_dimensions[current_row].height = 22

                for col_idx, val in enumerate(row, start=1):
                    col_name = columns[col_idx - 1].lower()
                    cell = ws.cell(row=current_row, column=col_idx)
                    
                    cell.border = full_border
                    cell.font = row_font if row_font else base_font

                    if row_fill:
                        cell.fill = row_fill

                    if "valor" in col_name and isinstance(val, (int, float)):
                        cell.value = val / 100.0 if isinstance(val, int) else val
                        cell.number_format = 'R$ #,##0.00'
                        cell.alignment = align_right
                    elif "data" in col_name:
                        cell.value = val
                        cell.alignment = align_center
                    elif isinstance(val, (int, float)):
                        cell.value = val
                        cell.number_format = '#,##0'
                        cell.alignment = align_right
                    else:
                        cell.value = val
                        cell.alignment = align_center if col_name.startswith("status") else align_left

                current_row += 1

        last_data_row = max(current_row - 1, 4)

        tab_range = f"A3:{last_col_letter}{last_data_row}"
        tab = Table(displayName="TabelaAuditoriaTRM", ref=tab_range)
        
        style = TableStyleInfo(
            name="TableStyleLight1",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=False,
            showColumnStripes=False
        )
        tab.tableStyleInfo = style
        ws.add_table(tab)

        ws.freeze_panes = "A4"

        for col in ws.columns:
            max_len = 0
            for cell in col:
                if cell.row in (1, 2):
                    continue
                
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)

            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 5, 15), 55)

        wb.save(self.output_xlsx_path)