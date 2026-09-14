from pathlib import Path

def get_xml_files_from_directory(directory_path: str):
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        return Error(f"Diretório inválido: {directory_path} --get_xml.py");

    pattern = "*.xml"
    xml_files = list(directory.rglob(pattern))

    if not xml_files:
        return Error(f"Nenhum arquivo XML encontrado no diretório: {directory_path} --get_xml.py")

    return xml_files
