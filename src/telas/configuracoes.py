"""Tela de Configurações, os detectores e, com a opção, os modelos."""

import html
import gradio as gr

from database import contrato_dados
from patologias import catalogo, modelos
from visual import desenho, estilo

OCULTO = gr.update(visible=False)
VISIVEL = gr.update(visible=True)
SEM_DETECTOR = "Nenhum detector cadastrado."
SEM_MODELO = "Nenhum modelo cadastrado."
IGNORAR = "(ignorar)"


def _decimal(valor):
    """Número com vírgula decimal, como na tela."""
    return str(valor).replace(".", ",")


def _inteiro_digitado(texto, campo):
    """Converte o texto digitado em inteiro, ou recusa dizendo o campo."""
    try:
        return int((texto or "").strip())
    except ValueError:
        raise ValueError(f"{campo}, digite um número inteiro.") from None


def _limiar_digitado(texto):
    """Converte o limiar digitado em número, aceitando vírgula."""
    try:
        return float((texto or "").strip().replace(",", "."))
    except ValueError:
        raise ValueError("Limiar, digite um número entre 0 e 1, como 0,42.") from None


def _aviso(texto, erro=False):
    """Aviso embaixo do formulário ou do detalhe, vermelho para erro e cinza para o resto."""
    if not texto:
        return ""
    classe = "pav-apoio"
    if erro:
        classe = "pav-aviso"
    return f'<div class="{classe}">{html.escape(texto)}</div>'


def _procurar_por_id(lista, identificador):
    """Item da lista com esse id, ou None."""
    for item in lista:
        if item["id"] == identificador:
            return item
    return None


def _ids(lista):
    """Ids da lista, na mesma ordem das linhas da tabela."""
    ids = []
    for item in lista:
        ids.append(item["id"])
    return ids


def _opcoes_da_norma(arvore_dnit):
    """Ignorar e todas as patologias do catálogo, em ordem de árvore, com recuo por nível."""
    opcoes = [("Ignorar", IGNORAR)]
    for identificador_dnit, profundidade in catalogo.em_ordem(arvore_dnit):
        recuo = "\u00a0" * 4 * profundidade
        codigos = ", ".join(catalogo.codigos(arvore_dnit, identificador_dnit))
        rotulo = catalogo.rotulo(arvore_dnit, identificador_dnit)
        opcoes.append((f"{recuo}{rotulo} ({codigos})", identificador_dnit))
    return opcoes


def _linhas_modelos(lista_modelos, problemas_de_carga):
    """Linhas da tabela, uma por modelo, com as etiquetas ao lado do nome."""
    linhas = []
    for modelo in lista_modelos:
        problema = problemas_de_carga.get(modelo["id"])
        linhas.append([html.escape(modelo["nome"]) + _etiquetas(modelo["fixo"], problema)])
    return linhas


def _detectores_que_usam(caminho_database, modelo_id):
    """Nomes dos detectores que usam o modelo."""
    nomes = []
    for detector in contrato_dados.detectores(caminho_database):
        if detector["modelo_id"] == modelo_id:
            nomes.append(detector["nome"])
    return nomes


def _descrever_modelo(caminho_database, arvore_dnit, problemas_de_carga, modelo, usam):
    """Cartão de detalhe do modelo."""
    if modelo is None:
        return _vazio(SEM_MODELO)
    problema = problemas_de_carga.get(modelo["id"])
    titulo = html.escape(modelo["nome"]) + _etiquetas(modelo["fixo"], problema)
    linha_de_apoio = ""
    if problema:
        linha_de_apoio = f'<div class="pav-aviso">{html.escape(problema)}</div>'
    corpo = (_correspondencia(caminho_database, arvore_dnit, modelo["id"])
             + _lista_simples("Arquivo", [modelo["caminho_arquivo_de_modelo"]], "pav-mono")
             + _lista_simples("Detectores que usam", usam))
    return _cartao("Detalhe do modelo", titulo, linha_de_apoio, corpo, "tres-secoes")


def _botao_remover_modelo(modelo, usam):
    """Fixo não tem botão; modelo em uso tem o botão desabilitado."""
    if modelo is None or modelo["fixo"]:
        return OCULTO
    return gr.update(visible=True, interactive=not usam)


def _linhas_detectores(detectores):
    """Linhas da tabela, uma por detector, com a etiqueta de fixo ao lado do nome."""
    linhas = []
    for detector in detectores:
        linhas.append([html.escape(detector["nome"]) + _etiquetas(detector["fixo"]),
                       detector["modelo_nome"],
                       f"{detector['resolucao_entrada']} px",
                       _decimal(detector["limiar_confianca"]),
                       str(detector["max_deteccoes"])])
    return linhas


def _descrever_detector(caminho_database, arvore_dnit, cores, detector):
    """Cartão de detalhe do detector."""
    if detector is None:
        return _vazio(SEM_DETECTOR)
    titulo = html.escape(detector["nome"]) + _etiquetas(detector["fixo"])
    linha_de_apoio = f'<div class="pav-apoio">Modelo: {html.escape(detector["modelo_nome"])}</div>'
    corpo = (_configuracao_de_inferencia(detector)
             + _patologias_com_cor(caminho_database, arvore_dnit, cores, detector["modelo_id"]))
    return _cartao("Detalhe do detector", titulo, linha_de_apoio, corpo)


def _botao_remover_detector(detector):
    """Remover aparece só para detector que não é fixo."""
    if detector is None or detector["fixo"]:
        return OCULTO
    return VISIVEL


def _opcoes_modelos(caminho_database, modelos_carregados):
    """Modelos que podem ser usados em detector."""
    opcoes = []
    for modelo in contrato_dados.modelos(caminho_database):
        if modelo["id"] in modelos_carregados:
            opcoes.append((modelo["nome"], modelo["id"]))
    return opcoes

# -------------------------------------------------------------- pedaços do cartão

def _cartao(rotulo_secao, titulo, linha_de_apoio, corpo, classe_corpo=""):
    """Moldura do detalhe, com rótulo, título, linha de apoio e corpo em colunas."""
    return (f'<div class="pav-cartao"><div class="pav-cartao-cabeca"><div>'
            f'{estilo.rotulo(rotulo_secao)}'
            f'<div class="pav-cartao-titulo">{titulo}</div>{linha_de_apoio}</div></div>'
            f'<div class="pav-cartao-corpo {classe_corpo}">{corpo}</div></div>')


def _vazio(texto):
    """Cartão sem conteúdo, para quando não há modelo ou detector cadastrado."""
    return f'<div class="pav-cartao"><p class="pav-apoio">{html.escape(texto)}</p></div>'


def _etiquetas(fixo, problema=None):
    """Etiquetas ao lado do nome, Fixo e, para modelo que não carregou, Indisponível."""
    etiquetas = ""
    if fixo:
        etiquetas = etiquetas + estilo.tag_fixo()
    if problema:
        etiquetas = etiquetas + estilo.tag_indisponivel(problema)
    return etiquetas


def _lista_simples(rotulo_secao, itens, classe=""):
    """Seção com um rótulo e uma lista de textos, um por linha."""
    linhas = []
    for item in itens:
        linhas.append(f'<span class="{classe}">{html.escape(item)}</span>')
    corpo = "".join(linhas)
    if not linhas:
        corpo = '<span class="pav-apoio">nenhum</span>'
    return (f'<div>{estilo.rotulo(rotulo_secao)}'
            f'<div class="pav-coluna">{corpo}</div></div>')


def _correspondencia(caminho_database, arvore_dnit, modelo_id):
    """Quadro classe do modelo → patologia da norma, com os códigos DNIT que a patologia cobre."""
    linhas = [f'<div class="linha cabeca">{estilo.rotulo("Classe no modelo")}<span></span>'
              f'{estilo.rotulo("Patologia DNIT")}{estilo.rotulo("Códigos")}</div>']
    for nome_da_classe, identificador_dnit in contrato_dados.classes(caminho_database, modelo_id).items():
        fora = ""
        codigos = []
        if identificador_dnit is None:
            destino = "ignorada"
            fora = " fora"
        elif catalogo.existe(arvore_dnit, identificador_dnit):
            destino = catalogo.rotulo(arvore_dnit, identificador_dnit)
            codigos = catalogo.codigos(arvore_dnit, identificador_dnit)
        else:
            destino = f"{identificador_dnit}, que não existe no catálogo"
        chips = []
        for codigo in codigos:
            chips.append(f'<span class="pav-chip">{html.escape(codigo)}</span>')
        linhas.append(f'<div class="linha"><span class="de{fora}">{html.escape(nome_da_classe)}</span>'
                      f'<span class="seta">→</span>'
                      f'<span class="para{fora}">{html.escape(destino)}</span>'
                      f'<span class="codigos">{"".join(chips)}</span></div>')
    return (f'<div>{estilo.rotulo("Classes e correspondência")}'
            f'<div class="pav-correspondencia">{"".join(linhas)}</div></div>')


def _configuracao_de_inferencia(detector):
    """Entrada, limiar e máximo de detecções do detector, lado a lado."""
    valores = [("Entrada", f"{detector['resolucao_entrada']} px"),
               ("Limiar", _decimal(detector["limiar_confianca"])),
               ("Máx. detecções", str(detector["max_deteccoes"]))]
    partes = []
    for rotulo, valor in valores:
        partes.append(f'<div>{estilo.rotulo(rotulo)}'
                      f'<div class="pav-receita-valor">{valor}</div></div>')
    return (f'<div>{estilo.rotulo("Configuração de inferência")}'
            f'<div class="pav-receita">{"".join(partes)}</div></div>')


def _patologias_com_cor(caminho_database, arvore_dnit, cores, modelo_id):
    """Patologias que o modelo detecta, cada uma com a cor do desenho na imagem."""
    vistas = []
    itens = []
    for identificador_dnit in contrato_dados.classes(caminho_database, modelo_id).values():
        if identificador_dnit is None or identificador_dnit in vistas:
            continue
        if not catalogo.existe(arvore_dnit, identificador_dnit):
            continue
        vistas.append(identificador_dnit)
        cor = cores.get(identificador_dnit, desenho.COR_FALLBACK)
        rotulo = catalogo.rotulo(arvore_dnit, identificador_dnit)
        itens.append(f'<span class="pav-classe-item"><span class="pav-amostra" '
                     f'style="background: rgb{cor}"></span>{html.escape(rotulo)}</span>')
    corpo = "".join(itens)
    if not itens:
        corpo = '<span class="pav-apoio">nenhuma</span>'
    return (f'<div>{estilo.rotulo("Patologias que detecta")}'
            f'<div class="pav-coluna">{corpo}</div></div>')


def montar(caminho_database,
            pasta_arquivos_de_modelos,
            arvore_dnit,
            modelos_carregados,
            problemas_de_carga,
            cores,
            gerenciar_modelos):
    """Monta a tela de Configurações e devolve a função que a relê, com entradas e saídas."""
    opcoes_norma = _opcoes_da_norma(arvore_dnit)

    # ---------------------------------------------------------------- modelos

    def selecionar_modelo(modelo_id, aviso=""):
        """Detalhe e id escolhido e, com a opção, os três botões e o aviso."""
        lista_modelos = contrato_dados.modelos(caminho_database)
        modelo = _procurar_por_id(lista_modelos, modelo_id)
        if modelo is None and lista_modelos:
            modelo = lista_modelos[0]
        escolhido = None
        usam = []
        if modelo is not None:
            escolhido = modelo["id"]
            usam = _detectores_que_usam(caminho_database, escolhido)
        saidas = [_descrever_modelo(caminho_database, arvore_dnit, problemas_de_carga, modelo, usam),
                  escolhido]
        if gerenciar_modelos:
            saidas.extend([_botao_remover_modelo(modelo, usam), OCULTO, OCULTO, aviso])
        return saidas

    def reler_modelos(modelo_id, aviso=""):
        """Tudo da subaba Modelos, relido do database."""
        lista_modelos = contrato_dados.modelos(caminho_database)
        return ([_linhas_modelos(lista_modelos, problemas_de_carga), _ids(lista_modelos)]
                + selecionar_modelo(modelo_id, aviso))

    def clicar_modelo(ids, evento: gr.SelectData):
        """Clicar em uma linha da tabela de modelos."""
        return selecionar_modelo(ids[evento.index[0]])

    def pedir_remocao_modelo(modelo_id):
        """Primeiro clique em Remover, troca o botão pela confirmação."""
        modelo = _procurar_por_id(contrato_dados.modelos(caminho_database), modelo_id)
        if modelo is None:
            return OCULTO, OCULTO, OCULTO, _aviso("Esse modelo não existe mais.", erro=True)
        return (OCULTO, VISIVEL, VISIVEL,
                _aviso(f"Remover o modelo {modelo['nome']}? O arquivo de modelo também é apagado."))

    def remover_modelo(modelo_id, detector_id):
        """Confirmação da remoção do modelo."""
        modelo = _procurar_por_id(contrato_dados.modelos(caminho_database), modelo_id)
        try:
            modelos.remover_arquivo_de_modelo(caminho_database, pasta_arquivos_de_modelos, modelo_id)
        except ValueError as erro:
            return reler(modelo_id, detector_id, aviso_modelo=_aviso(str(erro), erro=True))
        modelos_carregados.pop(modelo_id, None)
        problemas_de_carga.pop(modelo_id, None)
        return reler(None, detector_id,
                     aviso_modelo=_aviso(f"Modelo {modelo['nome']} removido, com o arquivo."))

    def ler_arquivo(caminho_arquivo):
        """Arquivo enviado, lê as classes que o modelo declara."""
        if not caminho_arquivo:
            return None, ""
        try:
            classes_no_modelo = modelos.ler_classes(modelos.abrir_modelo(caminho_arquivo))
        except ValueError as erro:
            return None, _aviso(str(erro), erro=True)
        nomes = list(classes_no_modelo.values())
        return nomes, _aviso(f"{len(nomes)} classes lidas. Escolha, para cada uma, a patologia "
                             "da norma ou Ignorar.")

    def esquecer_arquivo():
        """Arquivo tirado do campo, descarta as classes lidas."""
        return None, ""

    def salvar(caminho_arquivo, nomes, nome_modelo, modelo_id, detector_id, *escolhas):
        """Botão Salvar modelo."""
        if not nomes:
            aviso = _aviso("Envie o arquivo de modelo antes de salvar.", erro=True)
            return [gr.skip(), gr.skip(), aviso] + reler(modelo_id, detector_id)
        faltando = []
        correspondencia = {}
        for nome_da_classe, escolha in zip(nomes, escolhas):
            if not escolha:
                faltando.append(nome_da_classe)
            elif escolha == IGNORAR:
                correspondencia[nome_da_classe] = None
            else:
                correspondencia[nome_da_classe] = escolha
        if faltando:
            aviso = _aviso(f"Falta escolher a patologia, ou Ignorar, para {', '.join(faltando)}.",
                           erro=True)
            return [gr.skip(), gr.skip(), aviso] + reler(modelo_id, detector_id)
        try:
            novo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta_arquivos_de_modelos,
                                                          arvore_dnit, caminho_arquivo, nome_modelo,
                                                          correspondencia)
        except ValueError as erro:
            return ([gr.skip(), gr.skip(), _aviso(str(erro), erro=True)]
                    + reler(modelo_id, detector_id))
        try:
            modelos_carregados[novo_id] = modelos.carregar_modelo_por_id(
                caminho_database, pasta_arquivos_de_modelos, arvore_dnit, novo_id)
            aviso = _aviso(f"Modelo {nome_modelo.strip()} cadastrado.")
        except ValueError as erro:
            problemas_de_carga[novo_id] = str(erro)
            aviso = _aviso(f"Modelo {nome_modelo.strip()} cadastrado, mas não carregou. {erro}",
                           erro=True)
        return [None, None, aviso] + reler(novo_id, detector_id)

    # ------------------------------------------------------------- detectores

    def selecionar_detector(detector_id, aviso=""):
        """Detalhe, id escolhido, os três botões e o aviso. Sem id válido, o primeiro da lista."""
        detectores = contrato_dados.detectores(caminho_database)
        detector = _procurar_por_id(detectores, detector_id)
        if detector is None and detectores:
            detector = detectores[0]
        escolhido = None
        if detector is not None:
            escolhido = detector["id"]
        return [_descrever_detector(caminho_database, arvore_dnit, cores, detector),
                escolhido,
                _botao_remover_detector(detector),
                OCULTO,
                OCULTO,
                aviso]

    def reler_detectores(detector_id, aviso=""):
        """Tudo da subaba Detectores, relido do database."""
        detectores = contrato_dados.detectores(caminho_database)
        opcoes = _opcoes_modelos(caminho_database, modelos_carregados)
        return ([_linhas_detectores(detectores), _ids(detectores)]
                + selecionar_detector(detector_id, aviso)
                + [gr.update(choices=opcoes)])

    def clicar_detector(ids, evento: gr.SelectData):
        """Clicar em uma linha da tabela de detectores."""
        return selecionar_detector(ids[evento.index[0]])

    def pedir_remocao_detector(detector_id):
        """Primeiro clique em Remover, troca o botão pela confirmação."""
        detector = _procurar_por_id(contrato_dados.detectores(caminho_database), detector_id)
        if detector is None:
            return OCULTO, OCULTO, OCULTO, _aviso("Esse detector não existe mais.", erro=True)
        return OCULTO, VISIVEL, VISIVEL, _aviso(f"Remover o detector {detector['nome']}?")

    def remover_detector(modelo_id, detector_id):
        """Confirmação da remoção do detector."""
        detector = _procurar_por_id(contrato_dados.detectores(caminho_database), detector_id)
        try:
            contrato_dados.remover_detector(caminho_database, detector_id)
        except ValueError as erro:
            return reler(modelo_id, detector_id, aviso_detector=_aviso(str(erro), erro=True))
        return reler(modelo_id, None,
                     aviso_detector=_aviso(f"Detector {detector['nome']} removido."))

    def criar(nome, modelo_id, resolucao, limiar, maximo, modelo_escolhido, detector_id):
        """Botão Criar detector."""
        try:
            if modelo_id is None or modelo_id not in modelos_carregados:
                raise ValueError("Escolha o modelo do detector.")
            novo_id = modelos.criar_detector(caminho_database,
                                             modelos_carregados[modelo_id],
                                             nome,
                                             modelo_id,
                                             _inteiro_digitado(resolucao, "Entrada"),
                                             _limiar_digitado(limiar),
                                             _inteiro_digitado(maximo, "Máximo de detecções"))
        except ValueError as erro:
            return ([nome, resolucao, limiar, maximo, _aviso(str(erro), erro=True)]
                    + reler(modelo_escolhido, detector_id))
        return (["", "", "", "", _aviso(f"Detector {nome.strip()} criado.")]
                + reler(modelo_escolhido, novo_id))

    # ------------------------------------------------------------- as duas

    def reler(modelo_id, detector_id, aviso_modelo="", aviso_detector=""):
        """Tudo das duas subabas, relido do database."""
        return reler_modelos(modelo_id, aviso_modelo) + reler_detectores(detector_id, aviso_detector)

    # --------------------------------------------------------------- montagem

    ids_modelos = gr.State([])
    escolhido_modelo = gr.State(None)
    ids_detectores = gr.State([])
    escolhido_detector = gr.State(None)
    classes_lidas = gr.State(None)

    with gr.Tabs():
        with gr.Tab("Modelos"):
            with gr.Row():
                with gr.Column(scale=2):
                    estilo.bloco('<h2 class="pav-secao-titulo">Modelos cadastrados</h2>')
                    lista_modelos = gr.Dataframe(value=[], headers=["Nome"], datatype=["html"],
                                                 show_label=False, interactive=False, buttons=[],
                                                 elem_classes="pav-lista")
                    detalhe_modelo = estilo.bloco("")
                    if gerenciar_modelos:
                        with gr.Row():
                            botao_remover_modelo = gr.Button("Remover", variant="stop", size="sm",
                                                             scale=0, min_width=110, visible=False)
                            botao_confirmar_modelo = gr.Button("Confirmar remoção", variant="stop",
                                                               size="sm", scale=0, min_width=170,
                                                               visible=False)
                            botao_cancelar_modelo = gr.Button("Cancelar", size="sm", scale=0,
                                                              min_width=110, visible=False)
                        aviso_remocao_modelo = estilo.bloco("")
                if gerenciar_modelos:
                    with gr.Column(scale=1):
                        estilo.bloco('<h2 class="pav-secao-titulo">Cadastrar modelo</h2>')
                        with gr.Column(elem_classes="pav-cartao"):
                            arquivo = gr.File(label="Arquivo do modelo (.pt)", file_types=[".pt"],
                                              type="filepath")

                            @gr.render(inputs=classes_lidas)
                            def desenhar_correspondencia(nomes):
                                if not nomes:
                                    return
                                rotulo = estilo.rotulo(f"Classes encontradas no arquivo, {len(nomes)}")
                                estilo.bloco(f'<div class="pav-bloco">{rotulo}</div>')
                                seletores = []
                                for nome_da_classe in nomes:
                                    seletores.append(gr.Dropdown(opcoes_norma, value=None,
                                                                 label=nome_da_classe,
                                                                 filterable=False))
                                nome_modelo = gr.Textbox(label="Nome do modelo", max_lines=1)
                                botao_salvar = gr.Button("Salvar modelo", variant="primary")
                                botao_salvar.click(salvar,
                                                   inputs=[arquivo, classes_lidas, nome_modelo,
                                                           escolhido_modelo, escolhido_detector] + seletores,
                                                   outputs=[arquivo, classes_lidas, aviso_cadastro] + tudo)

                            aviso_cadastro = estilo.bloco("")

        with gr.Tab("Detectores"):
            with gr.Row():
                with gr.Column(scale=2):
                    estilo.bloco('<h2 class="pav-secao-titulo">Detectores cadastrados</h2>')
                    lista_detectores = gr.Dataframe(value=[],
                                                    headers=["Nome", "Modelo", "Entrada", "Limiar", "Máx. det."],
                                                    datatype=["html", "str", "str", "str", "str"],
                                                    column_widths=["28%", "30%", "14%", "14%", "14%"],
                                                    show_label=False, interactive=False, buttons=[],
                                                    elem_classes="pav-lista")
                    detalhe_detector = estilo.bloco("")
                    with gr.Row():
                        botao_remover_detector = gr.Button("Remover", variant="stop", size="sm",
                                                           scale=0, min_width=110, visible=False)
                        botao_confirmar_detector = gr.Button("Confirmar remoção", variant="stop",
                                                             size="sm", scale=0, min_width=170,
                                                             visible=False)
                        botao_cancelar_detector = gr.Button("Cancelar", size="sm", scale=0,
                                                            min_width=110, visible=False)
                    aviso_remocao_detector = estilo.bloco("")
                with gr.Column(scale=1):
                    estilo.bloco('<h2 class="pav-secao-titulo">Criar detector</h2>')
                    with gr.Column(elem_classes="pav-cartao"):
                        nome = gr.Textbox(label="Nome do detector", max_lines=1)
                        modelo_do_detector = gr.Dropdown([], value=None, label="Modelo", filterable=False)
                        with gr.Row():
                            resolucao = gr.Textbox(label="Entrada (px)", max_lines=1, placeholder="em pixels")
                            limiar = gr.Textbox(label="Limiar", max_lines=1, placeholder="entre 0 e 1")
                            maximo = gr.Textbox(label="Máx. det.", max_lines=1, placeholder="a partir de 1")
                        botao_criar = gr.Button("Criar detector", variant="primary")
                        aviso_criacao = estilo.bloco("")

    saidas_selecao_modelo = [detalhe_modelo, escolhido_modelo]
    if gerenciar_modelos:
        saidas_selecao_modelo.extend([botao_remover_modelo, botao_confirmar_modelo,
                                      botao_cancelar_modelo, aviso_remocao_modelo])
    saidas_selecao_detector = [detalhe_detector, escolhido_detector, botao_remover_detector,
                               botao_confirmar_detector, botao_cancelar_detector, aviso_remocao_detector]
    tudo = ([lista_modelos, ids_modelos] + saidas_selecao_modelo
            + [lista_detectores, ids_detectores] + saidas_selecao_detector + [modelo_do_detector])

    lista_modelos.select(clicar_modelo,
                        inputs=ids_modelos,
                        outputs=saidas_selecao_modelo)
    lista_detectores.select(clicar_detector, inputs=ids_detectores, outputs=saidas_selecao_detector)
    botao_criar.click(criar,
                      inputs=[nome, modelo_do_detector, resolucao, limiar, maximo, escolhido_modelo, escolhido_detector],
                      outputs=[nome, resolucao, limiar, maximo, aviso_criacao] + tudo)
    botao_remover_detector.click(pedir_remocao_detector,
                                inputs=escolhido_detector,
                                 outputs=[botao_remover_detector, botao_confirmar_detector,botao_cancelar_detector, aviso_remocao_detector])
    botao_confirmar_detector.click(remover_detector,
                                    inputs=[escolhido_modelo, escolhido_detector],
                                   outputs=tudo)
    botao_cancelar_detector.click(selecionar_detector,
                                    inputs=escolhido_detector,
                                  outputs=saidas_selecao_detector)

    if gerenciar_modelos:
        botao_remover_modelo.click(pedir_remocao_modelo,
                                    inputs=escolhido_modelo,
                                   outputs=[botao_remover_modelo, botao_confirmar_modelo, botao_cancelar_modelo, aviso_remocao_modelo])
        botao_confirmar_modelo.click(remover_modelo,
                                    inputs=[escolhido_modelo, escolhido_detector],
                                     outputs=tudo)
        botao_cancelar_modelo.click(selecionar_modelo,
                                    inputs=escolhido_modelo,
                                    outputs=saidas_selecao_modelo)
        arquivo.upload(ler_arquivo,
                        inputs=arquivo,
                        outputs=[classes_lidas, aviso_cadastro])
        arquivo.clear(esquecer_arquivo, outputs=[classes_lidas, aviso_cadastro])

    return reler, [escolhido_modelo, escolhido_detector], tudo
