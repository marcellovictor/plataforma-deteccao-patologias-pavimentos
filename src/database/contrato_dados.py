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

def _inteiro(valor):
    """Checagem se é inteiro (e não booleano)"""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _numero(valor):
    """Checagem se é inteiro ou decimal (e não booleano)"""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


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


def detectores(caminho):
    """Todos os detectores, em ordem de id."""
    return implementacao.detectores(caminho)


def criar_detector(caminho, nome, modelo_id, resolucao_entrada, limiar_confianca, max_deteccoes):
    """Grava um detector e devolve o id."""
    nome = _nome(nome, "detector")
    if not _inteiro(resolucao_entrada) or resolucao_entrada <= 0:
        raise ValueError("A resolução de entrada é um número inteiro de pixels, acima de 0.")
    if not _numero(limiar_confianca) or not 0 <= limiar_confianca <= 1:
        raise ValueError("O limiar de confiança é um número entre 0 e 1.")
    if not _inteiro(max_deteccoes) or max_deteccoes < 1:
        raise ValueError("O máximo de detecções é um número inteiro, a partir de 1.")
    return implementacao.criar_detector(caminho, nome, modelo_id, resolucao_entrada, limiar_confianca, max_deteccoes)
