from src.services.get_xml import get_xml_files_from_directory

def test_get_xml_files_success_root_directory(tmp_path):
    """Garante a busca correta de arquivos XML no diretório informado."""
    file1 = tmp_path / "nota1.xml"
    file2 = tmp_path / "nota2.xml"
    file_txt = tmp_path / "ignore.txt"

    file1.touch()
    file2.touch()
    file_txt.touch()

    result = get_xml_files_from_directory(str(tmp_path))

    assert isinstance(result, list)
    assert len(result) == 2
    assert set(result) == {file1, file2}

def test_get_xml_files_recursive_search(tmp_path):
    """Valida se a busca encontra arquivos XML em subdiretórios (devido ao rglob)."""
    sub_dir = tmp_path / "2026" / "09"
    sub_dir.mkdir(parents=True)

    xml_root = tmp_path / "root.xml"
    xml_sub = sub_dir / "sub.xml"

    xml_root.touch()
    xml_sub.touch()

    result = get_xml_files_from_directory(str(tmp_path))

    assert len(result) == 2
    assert set(result) == {xml_root, xml_sub}

def test_get_xml_files_empty_directory(tmp_path):
    """Valida a mensagem de erro retornada quando não há nenhum arquivo XML no diretório."""
    dir_path = str(tmp_path)
    result = get_xml_files_from_directory(dir_path)

    expected_msg = f"Nenhum arquivo XML encontrado no diretório: {dir_path} --get_xml.py"
    assert result == expected_msg


def test_get_xml_files_directory_does_not_exist(tmp_path, capsys):
    """Garante o aviso impresso no console quando o caminho do diretório não existe."""
    invalid_path = str(tmp_path / "pasta_inexistente")

    result = get_xml_files_from_directory(invalid_path)

    captured = capsys.readouterr()
    assert f"Diretório inválido: {invalid_path} --get_xml.py" in captured.out
    assert result is None


def test_get_xml_files_path_is_a_file_not_dir(tmp_path, capsys):
    """Valida o comportamento ao passar o caminho de um arquivo em vez de um diretório."""
    file_path = tmp_path / "arquivo.txt"
    file_path.touch()

    result = get_xml_files_from_directory(str(file_path))

    captured = capsys.readouterr()
    assert f"Diretório inválido: {file_path} --get_xml.py" in captured.out
    assert result is None
