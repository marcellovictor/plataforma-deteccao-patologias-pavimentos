"""Tela de Informações, o quadro de patologias da norma."""

from html import escape

from visual import estilo

# Largura em pixels das colunas da hierarquia, da esquerda para a direita.
# A última coluna da hierarquia não entra aqui, fica com o que sobrar.
LARGURAS = (148, 118, 124)


def _folhas(arvore_dnit, identificador):
    """Quantas folhas existem abaixo do nó, ou 1 se ele mesmo é folha."""
    filhos = arvore_dnit["patologias"][identificador]["filhos"]
    if not filhos:
        return 1
    total = 0
    for filho in filhos:
        total = total + _folhas(arvore_dnit, filho)
    return total


def _niveis(arvore_dnit, identificador):
    """Quantos níveis há abaixo do nó até a folha mais funda."""
    filhos = arvore_dnit["patologias"][identificador]["filhos"]
    if not filhos:
        return 0
    fundos = []
    for filho in filhos:
        fundos.append(_niveis(arvore_dnit, filho))
    return 1 + max(fundos)


def _texto(no):
    """Nome do nó, com a descrição embaixo quando ela existe."""
    if no["descricao"]:
        return (escape(no["nome"])
                + f'<div class="pav-norma-descricao">{escape(no["descricao"])}</div>')
    return escape(no["nome"])


def _linhas(arvore_dnit, identificador, nivel, colunas, antes, linhas):
    """Percorre o ramo e acrescenta uma linha da tabela por folha."""
    no = arvore_dnit["patologias"][identificador]
    if no["filhos"]:
        span = _folhas(arvore_dnit, identificador)
        rowspan = f' rowspan="{span}"' if span > 1 else ""
        celula = f'<td{rowspan} class="grupo">{_texto(no)}</td>'
        primeiro = True
        for filho in no["filhos"]:
            _linhas(arvore_dnit, filho, nivel + 1, colunas,
                    antes + celula if primeiro else "", linhas)
            primeiro = False
        return
    resto = colunas - nivel + 1
    colspan = f' colspan="{resto}"' if resto > 1 else ""
    linhas.append(f"<tr>{antes}<td{colspan}>{_texto(no)}</td>"
                  f'<td class="cod">{escape(no["codigo"] or "")}</td></tr>')


def _larguras_das_colunas(colunas):
    """Marcação das larguras, fixas na hierarquia e na codificação, livre na última da hierarquia."""
    partes = []
    for indice in range(colunas - 1):
        largura = LARGURAS[min(indice, len(LARGURAS) - 1)]
        partes.append(f'<col style="width: {largura}px">')
    partes.append('<col><col class="cod">')
    return f'<colgroup>{"".join(partes)}</colgroup>'


def _tabela(arvore_dnit, raiz):
    """Uma tabela por nó de primeiro nível, uma linha por folha."""
    colunas = max(1, _niveis(arvore_dnit, raiz))
    linhas = []
    for filho in arvore_dnit["patologias"][raiz]["filhos"]:
        _linhas(arvore_dnit, filho, 1, colunas, "", linhas)
    titulo = escape(arvore_dnit["patologias"][raiz]["nome"])
    return (f'<table class="pav-norma">{_larguras_das_colunas(colunas)}'
            f'<thead><tr><th colspan="{colunas}">{titulo}</th>'
            f"<th>Codificação</th></tr></thead>"
            f'<tbody>{"".join(linhas)}</tbody></table>')


def quadro(arvore_dnit):
    """O quadro inteiro, na ordem do catálogo, com a fonte no fim."""
    tabelas = []
    for raiz in arvore_dnit["raizes"]:
        tabelas.append(_tabela(arvore_dnit, raiz))
    return ("".join(tabelas)
            + f'<p class="pav-apoio pav-norma-fonte">Fonte: {escape(arvore_dnit["fonte"])}. '
              "As colunas de classe das fendas (FC-1 a FC-3) ficam de fora: dependem de medir "
              "a abertura da trinca em milímetros, o que não se obtém de bounding box.</p>")


def montar(arvore_dnit):
    """Monta a tela de Informações."""
    estilo.bloco('<h2 class="pav-secao-titulo">Guia de patologias da norma</h2>'
                 '<p class="pav-secao-texto pav-norma-intro">Quadro resumo das patologias e da '
                 'codificação, conforme a norma.</p>' + quadro(arvore_dnit))
