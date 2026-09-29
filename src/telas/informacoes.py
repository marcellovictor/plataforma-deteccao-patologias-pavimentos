"""Tela de Informações, o quadro de patologias da norma."""

from html import escape

import gradio as gr


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
        return escape(no["nome"]) + "<br><small>" + escape(no["descricao"]) + "</small>"
    return escape(no["nome"])


def _linhas(arvore_dnit, identificador, nivel, colunas, antes, linhas):
    """Percorre o ramo e acrescenta uma linha da tabela por folha."""
    no = arvore_dnit["patologias"][identificador]
    if no["filhos"]:
        span = _folhas(arvore_dnit, identificador)
        rowspan = f' rowspan="{span}"' if span > 1 else ""
        celula = f"<td{rowspan}>{_texto(no)}</td>"
        primeiro = True
        for filho in no["filhos"]:
            _linhas(arvore_dnit, filho, nivel + 1, colunas,
                    antes + celula if primeiro else "", linhas)
            primeiro = False
        return
    resto = colunas - nivel + 1
    colspan = f' colspan="{resto}"' if resto > 1 else ""
    linhas.append(f"<tr>{antes}<td{colspan}>{_texto(no)}</td>"
                  f"<td>{escape(no['codigo'] or '')}</td></tr>")


def _tabela(arvore_dnit, raiz):
    """Uma tabela por nó de primeiro nível, uma linha por folha."""
    colunas = max(1, _niveis(arvore_dnit, raiz))
    linhas = []
    for filho in arvore_dnit["patologias"][raiz]["filhos"]:
        _linhas(arvore_dnit, filho, 1, colunas, "", linhas)
    titulo = escape(arvore_dnit["patologias"][raiz]["nome"])
    return (f'<table border="1" cellpadding="4">'
            f'<thead><tr><th colspan="{colunas}">{titulo}</th>'
            f"<th>Codificação</th></tr></thead>"
            f'<tbody>{"".join(linhas)}</tbody></table><br>')


def quadro(arvore_dnit):
    """O quadro inteiro, na ordem do catálogo, com a fonte no fim."""
    tabelas = []
    for raiz in arvore_dnit["raizes"]:
        tabelas.append(_tabela(arvore_dnit, raiz))
    return ("".join(tabelas)
            + f'<p><small>Fonte: {escape(arvore_dnit["fonte"])}. As colunas de classe das '
              "fendas (FC-1 a FC-3) ficam de fora: dependem de medir a abertura da trinca em "
              "milímetros, o que não se obtém de bounding box.</small></p>")


def montar(arvore_dnit):
    """Monta a tela de Informações."""
    gr.Markdown("## Guia de patologias da norma")
    gr.Markdown("Quadro resumo das patologias e da codificação, conforme a norma.")
    gr.HTML(quadro(arvore_dnit))