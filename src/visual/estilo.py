"""Aparência da plataforma, com as cores, o tema do Gradio, o CSS e os pedaços de HTML repetidos."""

import html
from pathlib import Path

import gradio as gr

PASTA_ICONES = Path(__file__).parent / "icones"

# Fonte única das cores. Delas saem o tema do Gradio, que pinta os componentes nativos,
# e as variáveis --pav-* do CSS, que pintam o HTML escrito por nós.
TOKENS = {
    "fundo": "#EBECEE",        # fundo da aplicação
    "faixa": "#E3E9F3",        # cabeçalho de tabela, ficha, fundos suaves
    "campo": "#FFFFFF",        # cartão, campo de formulário, corpo de tabela
    "borda": "#BFCADC",        # moldura visível
    "hairline": "#D9E0EC",     # divisória entre linhas
    "tinta": "#141C2B",        # texto principal
    "tinta_2": "#2E3A50",      # texto secundário (9,7:1 no fundo claro)
    "tinta_3": "#55627A",      # rótulos e apoio (5,2:1 no fundo claro)
    "tinta_4": "#8791A5",      # placeholder, mais claro que o rótulo (3,2:1 no campo branco)
    "acao": "#3B62A8",         # ação principal e navegação (texto branco a 6,0:1)
    "acao_forte": "#2F5190",   # ação principal, sob o cursor
    "acao_texto": "#FFFFFF",
    "remover_tinta": "#8A2B12",
    "remover_borda": "#C9A392",
    "cabecalho": "#263A5E",          # faixa do topo da página
    "cabecalho_tinta": "#F4F7FC",    # título e botões sobre a faixa (10,6:1)
    "cabecalho_rotulo": "#AEBCD6",   # rótulo pequeno sobre a faixa (5,9:1)
    "cabecalho_linha": "#6C8FCB",    # linha embaixo da faixa
}

FONTE = gr.themes.GoogleFont("IBM Plex Sans")
FONTE_MONO = gr.themes.GoogleFont("IBM Plex Mono")


def _valores_do_tema():
    """Cores do tema do Gradio, com o mesmo valor no modo claro e no escuro."""
    valores_claros = {
        "body_background_fill": TOKENS["fundo"],
        "background_fill_primary": TOKENS["campo"],
        "background_fill_secondary": TOKENS["faixa"],
        "block_background_fill": TOKENS["campo"],
        "panel_background_fill": TOKENS["faixa"],
        "block_border_color": TOKENS["borda"],
        "panel_border_color": TOKENS["borda"],
        "border_color_primary": TOKENS["borda"],
        "border_color_accent": TOKENS["acao"],
        "body_text_color": TOKENS["tinta"],
        "body_text_color_subdued": TOKENS["tinta_3"],
        "block_label_text_color": TOKENS["tinta_3"],
        "block_title_text_color": TOKENS["tinta_2"],
        "block_info_text_color": TOKENS["tinta_3"],
        "input_background_fill": TOKENS["campo"],
        "input_border_color": TOKENS["borda"],
        "input_border_color_focus": TOKENS["acao"],
        # O tema Base nasce com os campos sem borda; com 1px o campo fica delimitado.
        "input_border_width": "1px",
        "input_placeholder_color": TOKENS["tinta_4"],
        "button_primary_background_fill": TOKENS["acao"],
        "button_primary_background_fill_hover": TOKENS["acao_forte"],
        "button_primary_border_color": TOKENS["acao"],
        "button_primary_text_color": TOKENS["acao_texto"],
        "button_secondary_background_fill": TOKENS["campo"],
        "button_secondary_background_fill_hover": TOKENS["faixa"],
        "button_secondary_border_color": TOKENS["borda"],
        "button_secondary_text_color": TOKENS["tinta_2"],
        # Variante "stop" do gr.Button, usada em remover e confirmar remoção.
        "button_cancel_background_fill": TOKENS["campo"],
        "button_cancel_background_fill_hover": TOKENS["faixa"],
        "button_cancel_border_color": TOKENS["remover_borda"],
        "button_cancel_border_color_hover": TOKENS["remover_tinta"],
        "button_cancel_text_color": TOKENS["remover_tinta"],
        "button_cancel_text_color_hover": TOKENS["remover_tinta"],
        "table_border_color": TOKENS["hairline"],
        "table_even_background_fill": TOKENS["campo"],
        "table_odd_background_fill": TOKENS["campo"],
        "table_text_color": TOKENS["tinta"],
        "table_row_focus": TOKENS["faixa"],
        "link_text_color": TOKENS["acao"],
        "link_text_color_hover": TOKENS["acao_forte"],
        "link_text_color_active": TOKENS["acao_forte"],
        "link_text_color_visited": TOKENS["acao"],
        "code_background_fill": TOKENS["faixa"],
        "stat_background_fill": TOKENS["acao"],
        "slider_color": TOKENS["acao"],
        "checkbox_background_color_selected": TOKENS["acao"],
        "checkbox_border_color_selected": TOKENS["acao"],
    }
    
    valores = {}
    for nome, valor in valores_claros.items():
        valores[nome] = valor
        valores[nome + "_dark"] = valor
    valores["color_accent"] = TOKENS["acao"]
    return valores


TEMA = gr.themes.Base(font=[FONTE, "system-ui", "sans-serif"],
                      font_mono=[FONTE_MONO, "ui-monospace", "monospace"]).set(**_valores_do_tema())

# O Gradio decide claro ou escuro pelo tema do sistema. Este trecho roda ao abrir a página e fixa o modo claro na URL.
FORCAR_MODO_CLARO = """
() => {
  const url = new URL(window.location);
  if (url.searchParams.get('__theme') !== 'light') {
    url.searchParams.set('__theme', 'light');
    window.location.replace(url.href);
  }
}
"""


def _variaveis_css():
    """Uma variável CSS --pav-* para cada cor dos TOKENS."""
    linhas = []
    for nome, valor in TOKENS.items():
        linhas.append(f"  --pav-{nome}: {valor};")
    return "\n".join(linhas)


# Texto comum, sem f-string, para as chaves do CSS ficarem simples. Só as variáveis, que saem dos TOKENS, são somadas no começo.
CSS = """
:root, .gradio-container {
""" + _variaveis_css() + """
}

.gradio-container {max-width: 100% !important; padding: 0 !important;
                    background: var(--pav-fundo) !important;
                    color: var(--pav-tinta) !important;}
/* No Gradio 6.28 o respiro da página (16px em cima, 32px nos lados) e o limite de
   largura ficam num elemento de dentro do container, o main com a classe app. */
.gradio-container .app {max-width: 100% !important; padding: 0 !important;}
.gradio-container .pav-html :is(h1,h2,h3,p) {margin: 0;}
footer {display: none !important;}

/* Todo texto do HTML escrito por nós nasce com a tinta principal: nada herda
   cor de link nem cor de tema. A regra vale só dentro de .pav-html, que é a
   marca dos blocos escritos por nós, e não encosta nos componentes nativos. */
.pav-html, .pav-html p, .pav-html span, .pav-html div, .pav-html td, .pav-html th,
.pav-html dt, .pav-html dd, .pav-html h1, .pav-html h2, .pav-html label,
.pav-html strong {color: var(--pav-tinta);}

/* ------------------------------------------------------------- cabeçalho */
.pav-cabecalho {background: var(--pav-cabecalho);
                 border-bottom: 3px solid var(--pav-cabecalho_linha);
                 padding: 14px 26px !important; align-items: center !important;
                 gap: 12px !important; flex-wrap: nowrap !important;}
.pav-titulo {line-height: 1.2; color: var(--pav-tinta); margin: 0; letter-spacing: -.01em;}
.pav-cabecalho .pav-rotulo {margin: 0 0 6px; color: var(--pav-cabecalho_rotulo) !important;}
.pav-cabecalho .pav-titulo {color: var(--pav-cabecalho_tinta);}
/* Os botões do cabeçalho ficam claros sobre a faixa escura, sem a borda cinza do tema. */
.pav-cabecalho button {background: var(--pav-cabecalho_tinta) !important;
                        border-color: var(--pav-cabecalho_tinta) !important;}
.pav-cabecalho button:hover {background: var(--pav-faixa) !important;
                              border-color: var(--pav-faixa) !important;}

/* ------------------------------------------------------------ tipografia */
.pav-tela {padding: 20px 26px 26px !important;}
.pav-rotulo {font-size: 11px; font-weight: 500; line-height: 1; letter-spacing: .08em;
              text-transform: uppercase; color: var(--pav-tinta_3) !important;}
.pav-mono {font-family: var(--font-mono);}
.pav-apoio {font-size: 12px; line-height: 1.5; color: var(--pav-tinta_2) !important;}
.pav-secao-titulo {line-height: 1.3; margin: 0 0 3px; color: var(--pav-tinta) !important;}
.pav-secao-texto {font-size: 12.5px; line-height: 1.5; margin: 0 0 12px;
                   color: var(--pav-tinta_2) !important;}
.pav-cartao {background: var(--pav-campo); border: 1px solid var(--pav-borda); border-radius: 3px;
              padding: 20px;}
.pav-divisor {border-top: 1px solid var(--pav-borda); margin: 28px 0 0; padding: 20px 0 0;}
.pav-bloco {margin: 18px 0 0;}

/* ---------------------------------------------------------------- etiquetas */
.pav-tag {display: inline-block; margin-left: 9px; padding: 2px 6px;
           border: 1px solid var(--pav-borda); border-radius: 2px; background: var(--pav-faixa);
           font-size: 10px; font-weight: 500; line-height: 1.4; letter-spacing: .06em;
           text-transform: uppercase; color: var(--pav-tinta_2) !important; vertical-align: middle;
           cursor: help; white-space: nowrap;}
.pav-tag-indisponivel {border-color: var(--pav-remover_borda); background: var(--pav-campo);
                        color: var(--pav-remover_tinta) !important;}
.pav-aviso {font-size: 12.5px; line-height: 1.5; color: var(--pav-remover_tinta) !important;
             margin: 5px 0 0;}

/* ------------------------------------------------------------------ análise */
.pav-linha-titulo {display: flex; align-items: baseline; justify-content: space-between;
                    gap: 10px; height: 14px; margin: 0 0 8px;}
.pav-linha-titulo > span {line-height: 1;}
.pav-legenda {display: flex; justify-content: space-between; gap: 10px; margin-top: 6px;
               font-family: var(--font-mono); font-size: 11.5px; line-height: 1.4;
               color: var(--pav-tinta_2) !important;}
.pav-legenda .nome {overflow: hidden; text-overflow: ellipsis; white-space: nowrap;}
.pav-ficha {display: flex; align-items: baseline; gap: 9px; padding: 9px 11px;
             background: var(--pav-faixa); border: 1px solid var(--pav-borda); border-radius: 3px;}
.pav-ficha-nome {font-size: 13.5px; font-weight: 600; line-height: 1.3;}
.pav-chips {display: flex; flex-wrap: wrap; gap: 6px; margin: 9px 0 0;}
.pav-chip {font-family: var(--font-mono); font-size: 11.5px; line-height: 1;
            color: var(--pav-tinta_2) !important; background: var(--pav-faixa);
            border: 1px solid var(--pav-borda); padding: 5px 7px;}
.pav-resumo-n {font-size: 15px; font-weight: 600; line-height: 1.3; margin: 0 0 12px;}
.pav-pares {display: grid; grid-template-columns: auto 1fr; gap: 7px 16px; font-size: 12.5px;
             line-height: 1.4; margin: 0;}
.pav-pares dt {color: var(--pav-tinta_3) !important; margin: 0;}
.pav-pares dd {margin: 0;}

/* ------------------------------------------- tabelas escritas por nós */
.pav-tabela {width: 100%; border-collapse: collapse; background: var(--pav-campo);}
.pav-tabela th {padding: 8px 10px; font-size: 10.5px; font-weight: 600; line-height: 1.2;
                 letter-spacing: .07em; text-transform: uppercase;
                 color: var(--pav-tinta_3) !important; background: var(--pav-campo);
                 text-align: left;}
.pav-tabela td {padding: 9px 10px; font-size: 12.5px; line-height: 1.35;}
.pav-tabela td.num {text-align: right; font-family: var(--font-mono); font-size: 12px;}
.pav-tabela td.pos {font-family: var(--font-mono); font-size: 11.5px;
                     color: var(--pav-tinta_2) !important; white-space: nowrap;}
.pav-tabela th.num {text-align: right; width: 76px;}
.pav-tabela th.pos {width: 142px;}
.pav-vazio {padding: 14px 12px;}
.pav-rolagem {max-height: 300px; overflow-y: auto; border: 1px solid var(--pav-borda);
               border-radius: 3px; background: var(--pav-campo);}
.pav-rolagem thead th {position: sticky; top: 0;}
.pav-cor {display: inline-block; width: 10px; height: 10px; margin-right: 8px;
           vertical-align: middle;}

/* --------------------------------------------- quadro do Anexo A da norma */
.pav-norma {width: 100%; border-collapse: collapse; background: var(--pav-campo);
             table-layout: fixed;}
.pav-norma th {padding: 8px 10px; font-size: 10.5px; font-weight: 600; line-height: 1.3;
                letter-spacing: .06em; text-transform: uppercase; color: var(--pav-tinta_2);
                background: var(--pav-faixa); text-align: center;}
.pav-norma td {padding: 8px 11px; font-size: 12.5px; line-height: 1.45;
                vertical-align: middle;}
.pav-norma td.grupo {font-weight: 500; font-size: 12px; background: var(--pav-faixa);
                      text-align: center;}
.pav-norma td.cod {font-family: var(--font-mono); font-size: 13px; font-weight: 500;
                    text-align: center; white-space: nowrap;}
.pav-norma-descricao {font-size: 12px; line-height: 1.45; margin: 3px 0 0;
                       color: var(--pav-tinta_2) !important;}

/* --------------------------------------------------- cartão de detalhe */
.pav-cartao-cabeca {display: flex; align-items: flex-start; justify-content: space-between;
                     gap: 20px; margin: 0 0 16px;}
.pav-cartao-titulo {font-size: 16px; font-weight: 600; line-height: 1.3; margin-top: 7px;}
.pav-cartao-corpo {display: grid; grid-template-columns: 1fr 240px; gap: 26px;
                    border-top: 1px solid var(--pav-hairline); padding: 16px 0 0;}
.pav-cartao-corpo.tres-secoes {grid-template-columns: minmax(0, 580px) auto auto;
                                justify-content: start; column-gap: 56px;}
.pav-coluna {display: flex; flex-direction: column; gap: 7px; margin-top: 11px;}
.pav-coluna span {font-size: 12.5px; line-height: 1.4;}
.pav-classe-item {display: flex; align-items: center; gap: 8px; font-size: 12.5px;
                   line-height: 1.3;}
.pav-amostra {width: 10px; height: 10px; display: block; flex: none;}
.pav-receita {display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px;
               max-width: 420px; margin-top: 11px;}
.pav-receita-valor {font-family: var(--font-mono); font-size: 13px; line-height: 1.3;
                     margin-top: 6px;}

/* ----------------------------------------------- correspondência de classes */
/* Uma linha por classe, em quatro colunas (classe do modelo, seta, patologia, códigos).
   Cada linha é uma subgrade da grade de fora, e assim as colunas ficam alinhadas entre as
   linhas e cada linha pode ter a própria divisória. */
.pav-correspondencia {display: grid; grid-template-columns: auto 14px minmax(0, 1fr) auto;
                       column-gap: 12px; max-width: 580px; margin-top: 11px;
                       border: 1px solid var(--pav-hairline); border-radius: 3px;}
.pav-correspondencia .linha {display: grid; grid-template-columns: subgrid; grid-column: 1 / -1;
                              align-items: center; padding: 7px 10px;
                              border-top: 1px solid var(--pav-hairline);}
.pav-correspondencia .linha.cabeca {border-top: 0; background: var(--pav-faixa);
                                     padding: 8px 10px;}
.pav-correspondencia .de {justify-self: start; font-family: var(--font-mono); font-size: 12px;
                           line-height: 1.2; padding: 3px 6px; background: var(--pav-faixa);
                           border: 1px solid var(--pav-borda); border-radius: 2px;}
.pav-correspondencia .seta {color: var(--pav-tinta_3) !important;}
.pav-correspondencia .para {font-size: 12.5px; line-height: 1.3;}
.pav-correspondencia .codigos {display: flex; flex-wrap: wrap; gap: 4px; justify-content: flex-end;}
.pav-correspondencia .fora {color: var(--pav-tinta_3) !important; font-style: italic;}
.pav-correspondencia .de.fora {background: none; border-style: dashed;}

/* ------------------------------------------- tela de Informações */
.pav-norma col.cod {width: 112px;}
.pav-norma-intro {max-width: 860px;}
.pav-norma-fonte {max-width: 900px;}
.pav-corresp-tabela {max-width: 900px;}
.pav-corresp-tabela th.lateral {width: 220px;}
.pav-corresp-tabela td.codigos {font-weight: 500;}
.pav-corresp-ignoradas {display: flex; align-items: baseline; gap: 10px; margin: 12px 0 0;}
.pav-corresp-nota {max-width: 900px;}

/* ------------------------- regras que precisam vencer o CSS do Gradio */
/* O bloco() pede apply_default_css=False, então o .prose do Gradio não entra nos
   nossos blocos. Ainda sobram as regras dele por elemento, com uma classe e um
   elemento no seletor (.gradio-container-6-28-0 h1, ... table, td, tr), que
   vencem uma classe nossa: h1 e h2 com font-size: inherit, table com margem, e
   a borda das tabelas. As regras abaixo são as nossas que caem em cima das
   dele: nomeiam o container e o bloco, ficam mais específicas e vencem sem
   !important. A primeira apaga borda e margem nas nossas tabelas; as seguintes
   põem as nossas, e são mais específicas que ela. */
/* O gr.HTML do Gradio 6.28 põe um respiro (--block-padding) em volta do conteúdo
   mesmo com padding=False. Sem zerar, os nossos blocos ficam recuados em relação
   aos componentes nativos. */
.pav-html .html-container, .pav-html.html-container {padding: 0 !important;}
.gradio-container .pav-html :is(.pav-tabela, .pav-norma),
.gradio-container .pav-html :is(.pav-tabela, .pav-norma) :is(tr, th, td) {border: 0; margin: 0;}
.gradio-container .pav-html .pav-norma + .pav-norma {margin: 18px 0 0;}
.gradio-container .pav-html .pav-titulo {font-size: 19px; font-weight: 600;}
.gradio-container .pav-html .pav-secao-titulo {font-size: 15px; font-weight: 600;}
.gradio-container .pav-html .pav-secao-texto {margin: 0 0 12px;}
.gradio-container .pav-html table.pav-tabela th {border-bottom: 1px solid var(--pav-borda);}
.gradio-container .pav-html table.pav-tabela td {border-bottom: 1px solid var(--pav-hairline);}
.gradio-container .pav-html table.pav-tabela tr:last-child td {border-bottom: 0;}
.gradio-container .pav-html table.pav-corresp-tabela {border: 1px solid var(--pav-borda);}
.gradio-container .pav-html table.pav-norma {border: 1px solid var(--pav-borda);}
.gradio-container .pav-html table.pav-norma th {border: 1px solid var(--pav-borda);}
.gradio-container .pav-html table.pav-norma td {border: 1px solid var(--pav-hairline);}
.gradio-container .pav-html .pav-norma-fonte {margin: 16px 0 0;}
.gradio-container .pav-html .pav-corresp-aviso {margin: 9px 0 0;}
.gradio-container .pav-html .pav-corresp-nota {margin: 9px 0 0;}

/* ----------------------------------- componentes nativos: ajuste de forma */
/* Cor e tipografia vêm do tema; aqui fica só a forma (cantos e espessura),
   que o tema não expõe por componente. */
.pav-analisar button {border-radius: 3px !important; padding: 13px 16px !important;
                       font-size: 14px !important; font-weight: 600 !important;}
.pav-volta button {background: none !important; border: 0 !important; box-shadow: none !important;
                    color: var(--pav-acao) !important; font-size: 13px !important;
                    font-weight: 400 !important; padding: 0 !important; text-align: left !important;}
.pav-volta button:hover {color: var(--pav-acao_forte) !important;}

/* Exceção anotada: a tabela do Gradio (gr.Dataframe) nasce em fonte monoespaçada,
   no cabeçalho e nas células, e o tema não tem token para isso. As nossas listas
   usam a fonte comum. */
.pav-lista, .pav-lista * {font-family: var(--font) !important;}

/* Exceção anotada: o tema não tem token para o texto da aba, então tamanho,
   cor da aba não selecionada e negrito da selecionada são definidos aqui. No
   Gradio 6.28 as abas ficam em .tab-container, e a cor e o traço da aba
   selecionada vêm do color_accent do tema. */
.tab-container button {color: var(--pav-tinta_2) !important; font-size: 13px !important;}
.tab-container button.selected {color: var(--pav-acao) !important; font-weight: 600 !important;}
"""


def bloco(conteudo, **extras):
    """gr.HTML sem moldura, sem respiro e sem o CSS padrão do Gradio, marcado como nosso."""
    classes = ["pav-html"]
    classes.extend(extras.pop("elem_classes", None) or [])
    # apply_default_css=False tira a classe .prose, com que o Gradio veste o que está dentro do bloco.
    return gr.HTML(conteudo, container=False, padding=False, apply_default_css=False,
                   elem_classes=classes, **extras)


def rotulo(texto):
    """Rótulo pequeno em caixa alta, acima de um campo ou de um bloco."""
    return f'<div class="pav-rotulo">{html.escape(texto)}</div>'


def linha_titulo(texto, direita=""):
    """Linha de título de bloco, com o rótulo à esquerda e um dado medido à direita."""
    return (f'<div class="pav-linha-titulo"><span class="pav-rotulo">{html.escape(texto)}</span>'
            f'<span class="pav-apoio pav-mono">{html.escape(direita)}</span></div>')


def tag_fixo():
    """Etiqueta de modelo ou detector fixo, com a explicação ao passar o cursor."""
    return ('<span class="pav-tag" title="Vem com a plataforma. Não pode ser removido pela '
            'tela.">Fixo</span>')


def tag_indisponivel(motivo):
    """Etiqueta de modelo que não carregou, com o motivo ao passar o cursor."""
    return (f'<span class="pav-tag pav-tag-indisponivel" title="{html.escape(motivo)}">'
            f'Indisponível</span>')
