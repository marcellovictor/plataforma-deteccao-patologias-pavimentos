"""Acesso a dados da plataforma, o contrato e a escolha de quem o implementa."""

from database import sqlite as implementacao    # ponto que define a implementação

DESTINO_PADRAO = implementacao.CAMINHO_PADRAO


def _nome(nome, coisa):
    """Recusa nome vazio e devolve o nome sem espaços nas pontas."""
    nome = (nome or "").strip()
    if not nome:
        raise ValueError(f"Dê um nome ao {coisa}.")
    return nome


def abrir(destino=DESTINO_PADRAO):
    """Prepara o destino para ler e gravar, e devolve o destino que ficou valendo."""
    return implementacao.abrir(destino)


def modelos(caminho):
    """Todos os modelos, em ordem de id."""
    return implementacao.modelos(caminho)


def cadastrar_modelo(caminho, nome, caminho_pesos, sha256):
    """Grava o modelo e devolve o id."""
    nome = _nome(nome, "modelo")
    return implementacao.cadastrar_modelo(caminho, nome, caminho_pesos, sha256)