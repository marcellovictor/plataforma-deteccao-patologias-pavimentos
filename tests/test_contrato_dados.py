"""Testes do acesso a dados."""

import pytest

from database import contrato_dados


def test_nasce_vazio(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    assert contrato_dados.modelos(caminho) == []


def test_cadastrar_devolve_id(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    identificador = contrato_dados.cadastrar_modelo(caminho, "Base", "/pesos/base.pt", "a" * 64)
    assert identificador == 1


def test_modelo_cadastrado_aparece_na_lista(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, "Base", "/pesos/base.pt", "a" * 64)
    guardados = contrato_dados.modelos(caminho)
    assert len(guardados) == 1
    assert guardados[0]["nome"] == "Base"


def test_nome_sem_espaco_nas_pontas(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, "  Base  ", "/pesos/base.pt", "a" * 64)
    assert contrato_dados.modelos(caminho)[0]["nome"] == "Base"


def test_nome_vazio_recusado(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, "   ", "/pesos/base.pt", "a" * 64)


def test_nome_repetido_recusado(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, "Base", "/pesos/base.pt", "a" * 64)
    with pytest.raises(ValueError):
        contrato_dados.cadastrar_modelo(caminho, "Base", "/outro.pt", "b" * 64)


def test_abrir_de_novo_nao_apaga(tmp_path):
    caminho = contrato_dados.abrir(tmp_path / "teste.db")
    contrato_dados.cadastrar_modelo(caminho, "Base", "/pesos/base.pt", "a" * 64)
    contrato_dados.abrir(tmp_path / "teste.db")
    assert len(contrato_dados.modelos(caminho)) == 1