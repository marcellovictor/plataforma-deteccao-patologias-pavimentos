"""Implementação SQLite do acesso a dados, o esquema, a conexão e o SQL."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).parents[2] / "plataforma.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS modelo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL UNIQUE,
    caminho_pesos TEXT    NOT NULL,
    sha256        TEXT    NOT NULL
) STRICT;
"""


@contextmanager
def _conexao(caminho):
    """Uma conexão por operação, numa transação, fechada no fim."""
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


def abrir(destino=CAMINHO_PADRAO):
    """Cria as tabelas que faltarem e devolve o caminho que ficou valendo."""
    caminho = Path(destino).expanduser().resolve()
    with _conexao(caminho) as con:
        con.executescript(SCHEMA)
    return caminho


def modelos(caminho):
    """Retorna todos os modelos, em ordem de id."""
    with _conexao(caminho) as con:
        linhas = con.execute(
            "SELECT id, nome, caminho_pesos, sha256 FROM modelo ORDER BY id")
        encontrados = []
        for linha in linhas:
            encontrados.append(dict(linha))
        return encontrados


def cadastrar_modelo(caminho, nome, caminho_pesos, sha256):
    """Grava o modelo e devolve o id."""
    try:
        with _conexao(caminho) as con:
            return con.execute(
                "INSERT INTO modelo (nome, caminho_pesos, sha256) VALUES (?, ?, ?)",
                (nome, str(caminho_pesos), sha256)).lastrowid
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Já existe um modelo com o nome {nome}.") from e