"""Carrega o catálogo da norma a partir do YAML."""

from pathlib import Path

import yaml

CAMINHO = Path(__file__).parent / "catalogo_dnit.yaml"


def carregar(caminho=CAMINHO):
    """Lê o YAML e devolve o catálogo (fonte, raízes e patologias por id)."""
    dados = yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))
    patologias = {}

    def ler(bruto):
        """Guarda um nó no dicionário patologias e segue pelos filhos. Devolve o id."""
        identificador = bruto["id"]
        patologias[identificador] = dict(nome=bruto["nome"],
                                         nome_exibicao=bruto.get("nome_exibicao"),
                                         descricao=bruto.get("descricao"),
                                         codigo=bruto.get("codigo"),
                                         filhos=[])
        filhos = []
        for filho in bruto.get("filhos", []):
            filhos.append(ler(filho))
        patologias[identificador]["filhos"] = filhos
        return identificador

    raizes = []
    for patologia in dados["patologias"]:
        raizes.append(ler(patologia))
    return dict(fonte=dados.get("fonte", ""), raizes=raizes, patologias=patologias)


def existe(catalogo, identificador):
    return identificador in catalogo["patologias"]


def rotulo(catalogo, identificador):
    """Texto da tela para o nó. O nome_exibicao, ou o nome literal da norma se não houver."""
    no = catalogo["patologias"][identificador]
    return no["nome_exibicao"] or no["nome"]


def codigos(catalogo, identificador):
    """Códigos da norma que o nó cobre: o dele, se é folha, ou os das folhas abaixo dele."""
    no = catalogo["patologias"][identificador]
    if no["codigo"]:
        return [no["codigo"]]
    encontrados = []
    for filho in no["filhos"]:
        encontrados.extend(codigos(catalogo, filho))
    return encontrados


def em_ordem(catalogo, identificadores=None, profundidade=0):
    """(id, profundidade) de cada nó, na ordem da árvore, com o pai antes dos filhos."""
    for identificador in catalogo["raizes"] if identificadores is None else identificadores:
        yield identificador, profundidade
        yield from em_ordem(catalogo,
                            catalogo["patologias"][identificador]["filhos"],
                            profundidade + 1)