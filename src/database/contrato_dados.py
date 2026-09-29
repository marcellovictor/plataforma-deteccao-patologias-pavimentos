"""Acesso a dados da plataforma, o contrato e a escolha de quem o implementa."""

from database import sqlite as implementacao    # ponto que define a implementação
from patologias import catalogo

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


def cadastrar_modelo(caminho, arvore_dnit, nome, caminho_pesos, sha256, correspondencia):
    """Grava o modelo e devolve o id."""
    nome = _nome(nome, "modelo")
    if not correspondencia:
        raise ValueError("O modelo não tem classes.")
    fora = []
    for identificador_dnit in correspondencia.values():
        if identificador_dnit is not None and not catalogo.existe(arvore_dnit, identificador_dnit):
            fora.append(identificador_dnit)
    if fora:
        raise ValueError(f"Nó inexistente no catálogo da norma: {', '.join(fora)}.")
    return implementacao.cadastrar_modelo(caminho, nome, caminho_pesos, sha256, correspondencia)


def classes(caminho, modelo_id):
    """Classes dos pesos do modelo, nome -> nó do catálogo, ou None se ignorada."""
    return implementacao.classes(caminho, modelo_id)