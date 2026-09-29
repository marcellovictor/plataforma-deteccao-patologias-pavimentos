"""Testes do acesso a dados."""

import pytest
from database import contrato_dados
from patologias import catalogo

CORRESPONDENCIA = {"D00": "trinca_longitudinal", "D40": "panela", "Repair": None}


@pytest.fixture
def arvore():
    """Árvore da norma."""
    return catalogo.carregar()


def test_nasce_vazio(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    assert contrato_dados.modelos(caminho) == []


def test_cadastrar_devolve_id(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    identificador = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)
    assert identificador == 1


def test_modelo_cadastrado_aparece_na_lista(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)
    guardados = contrato_dados.modelos(caminho)
    assert len(guardados) == 1
    assert guardados[0]["nome"] == "Base"


def test_nome_sem_espaco_nas_pontas(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, arvore, "  Base  ", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)
    assert contrato_dados.modelos(caminho)[0]["nome"] == "Base"


def test_nome_vazio_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, arvore, "   ", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)


def test_nome_repetido_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/outro.pt", "b" * 64, CORRESPONDENCIA)


def test_abrir_de_novo_nao_apaga(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/pesos/base.pt", "a" * 64, CORRESPONDENCIA)
    contrato_dados.abrir(tmp_path / "teste.db")
    assert len(contrato_dados.modelos(caminho)) == 1


def test_classes_voltam_na_ordem_do_cadastro(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Vencedor", "/venc.pt", "a" * 64, CORRESPONDENCIA)
    guardadas = contrato_dados.classes(caminho, modelo_id)
    assert list(guardadas) == list(CORRESPONDENCIA)


def test_classe_ignorada_fica_sem_no(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Vencedor", "/venc.pt", "a" * 64, CORRESPONDENCIA)
    assert contrato_dados.classes(caminho, modelo_id)["Repair"] is None


def test_modelo_sem_classes_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, arvore, "Vazio", "/x.pt", "a" * 64, {})


def test_no_fora_do_catalogo_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, arvore, "Errado", "/x.pt", "a" * 64, {"X": "nao_existe"})


def test_detector_criado_aparece_na_lista(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/base.pt", "a" * 64, CORRESPONDENCIA)
    contrato_dados.criar_detector(caminho, "Cenário base", modelo_id, 640, 0.25, 300)
    guardados = contrato_dados.detectores(caminho)
    assert len(guardados) == 1
    assert guardados[0]["nome"] == "Cenário base"


def test_detector_traz_o_nome_do_modelo(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/base.pt", "a" * 64, CORRESPONDENCIA)
    contrato_dados.criar_detector(caminho, "Cenário base", modelo_id, 640, 0.25, 300)
    assert contrato_dados.detectores(caminho)[0]["modelo_nome"] == "Base"


def test_limiar_fora_da_faixa_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/base.pt", "a" * 64, CORRESPONDENCIA)
    with pytest.raises(ValueError):
        contrato_dados.criar_detector(caminho, "X", modelo_id, 640, 1.5, 300)


def test_limiar_booleano_recusado(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/base.pt", "a" * 64, CORRESPONDENCIA)
    with pytest.raises(ValueError):
        contrato_dados.criar_detector(caminho, "X", modelo_id, 640, True, 300)


def test_resolucao_fracionaria_recusada(tmp_path, arvore):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    modelo_id = contrato_dados.cadastrar_modelo(caminho, arvore, "Base", "/base.pt", "a" * 64, CORRESPONDENCIA)
    with pytest.raises(ValueError):
        contrato_dados.criar_detector(caminho, "X", modelo_id, 640.0, 0.25, 300)
