"""Tela de Configurações, os detectores e, com a opção, os modelos."""

import gradio as gr

from database import contrato_dados
from patologias import catalogo, modelos

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


def _nome_do_modelo(modelo, problemas_de_carga):
    """Nome do modelo, com fixo e indisponível marcados."""
    nome = modelo["nome"]
    if modelo["fixo"]:
        nome = f"{nome} (fixo)"
    if modelo["id"] in problemas_de_carga:
        nome = f"{nome} (indisponível)"
    return nome


def _linhas_modelos(lista_modelos, problemas_de_carga):
    """Linhas da tabela, uma por modelo."""
    linhas = []
    for modelo in lista_modelos:
        linhas.append([_nome_do_modelo(modelo, problemas_de_carga)])
    return linhas


def _detectores_que_usam(caminho_database, modelo_id):
    """Nomes dos detectores que usam o modelo."""
    nomes = []
    for detector in contrato_dados.detectores(caminho_database):
        if detector["modelo_id"] == modelo_id:
            nomes.append(detector["nome"])
    return nomes


def _descrever_modelo(caminho_database, arvore_dnit, problemas_de_carga, modelo, usam):
    """Detalhe do modelo, em texto."""
    if modelo is None:
        return SEM_MODELO
    partes = [f"### {_nome_do_modelo(modelo, problemas_de_carga)}",
              f"**Arquivo:** {modelo['caminho_arquivo_de_modelo']}"]
    if modelo["id"] in problemas_de_carga:
        partes.append(f"**Indisponível:** {problemas_de_carga[modelo['id']]}")
    correspondencia = "**Classes e correspondência:**"
    for nome_da_classe, identificador_dnit in contrato_dados.classes(caminho_database, modelo["id"]).items():
        if identificador_dnit is None:
            destino = "ignorada"
        elif catalogo.existe(arvore_dnit, identificador_dnit):
            destino = catalogo.rotulo(arvore_dnit, identificador_dnit)
        else:
            destino = f"{identificador_dnit}, que não existe no catálogo"
        correspondencia = f"{correspondencia}\n- {nome_da_classe} → {destino}"
    partes.append(correspondencia)
    texto_usam = "nenhum"
    if usam:
        texto_usam = ", ".join(usam)
    partes.append(f"**Detectores que usam:** {texto_usam}")
    return "\n\n".join(partes)


def _botao_remover_modelo(modelo, usam):
    """Fixo não tem botão; modelo em uso tem o botão desabilitado."""
    if modelo is None or modelo["fixo"]:
        return OCULTO
    return gr.update(visible=True, interactive=not usam)


def _linhas_detectores(detectores):
    """Linhas da tabela, uma por detector, com o fixo marcado no nome."""
    linhas = []
    for detector in detectores:
        nome = detector["nome"]
        if detector["fixo"]:
            nome = f"{nome} (fixo)"
        linhas.append([nome,
                       detector["modelo_nome"],
                       f"{detector['resolucao_entrada']} px",
                       _decimal(detector["limiar_confianca"]),
                       str(detector["max_deteccoes"])])
    return linhas


def _patologias_do_modelo(caminho_database, arvore_dnit, modelo_id):
    """Patologias que o modelo detecta."""
    rotulos = []
    for identificador_dnit in contrato_dados.classes(caminho_database, modelo_id).values():
        if identificador_dnit is not None and catalogo.existe(arvore_dnit, identificador_dnit):
            rotulo = catalogo.rotulo(arvore_dnit, identificador_dnit)
            if rotulo not in rotulos:
                rotulos.append(rotulo)
    return rotulos


def _descrever_detector(caminho_database, arvore_dnit, detector):
    """Detalhe do detector, em texto."""
    if detector is None:
        return SEM_DETECTOR
    nome = detector["nome"]
    if detector["fixo"]:
        nome = f"{nome} (fixo)"
    patologias = _patologias_do_modelo(caminho_database, arvore_dnit, detector["modelo_id"])
    texto_patologias = "nenhuma"
    if patologias:
        texto_patologias = ", ".join(patologias)
    return (f"### {nome}\n"
            f"**Modelo:** {detector['modelo_nome']}  \n"
            f"**Configuração de inferência:** entrada {detector['resolucao_entrada']} px · "
            f"limiar {_decimal(detector['limiar_confianca'])} · "
            f"máx. {detector['max_deteccoes']} detecções  \n"
            f"**Patologias que detecta:** {texto_patologias}")


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


def montar(caminho_database, pasta_arquivos_de_modelos, arvore_dnit,
           modelos_carregados, problemas_de_carga, gerenciar_modelos):
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
            return OCULTO, OCULTO, OCULTO, "Esse modelo não existe mais."
        return (OCULTO, VISIVEL, VISIVEL,
                f"Remover o modelo {modelo['nome']}? O arquivo de modelo também é apagado.")

    def remover_modelo(modelo_id, detector_id):
        """Confirmação da remoção do modelo."""
        modelo = _procurar_por_id(contrato_dados.modelos(caminho_database), modelo_id)
        try:
            modelos.remover_arquivo_de_modelo(caminho_database, pasta_arquivos_de_modelos, modelo_id)
        except ValueError as erro:
            return reler(modelo_id, detector_id, aviso_modelo=str(erro))
        modelos_carregados.pop(modelo_id, None)
        problemas_de_carga.pop(modelo_id, None)
        return reler(None, detector_id,
                     aviso_modelo=f"Modelo {modelo['nome']} removido, com o arquivo.")

    def ler_arquivo(caminho_arquivo):
        """Arquivo enviado, lê as classes que o modelo declara."""
        if not caminho_arquivo:
            return None, ""
        try:
            classes_no_modelo = modelos.ler_classes(modelos.abrir_modelo(caminho_arquivo))
        except ValueError as erro:
            return None, str(erro)
        nomes = list(classes_no_modelo.values())
        return nomes, (f"{len(nomes)} classes lidas. Escolha, para cada uma, a patologia da norma ou Ignorar.")

    def esquecer_arquivo():
        """Arquivo tirado do campo, descarta as classes lidas."""
        return None, ""

    def salvar(caminho_arquivo, nomes, nome_modelo, modelo_id, detector_id, *escolhas):
        """Botão Salvar modelo."""
        if not nomes:
            return [gr.skip(), gr.skip(), "Envie o arquivo de modelo antes de salvar."] + reler(modelo_id, detector_id)
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
            texto = f"Falta escolher a patologia, ou Ignorar, para {', '.join(faltando)}."
            return [gr.skip(), gr.skip(), texto] + reler(modelo_id, detector_id)
        try:
            novo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta_arquivos_de_modelos,
                                                          arvore_dnit, caminho_arquivo, nome_modelo,
                                                          correspondencia)
        except ValueError as erro:
            return [gr.skip(), gr.skip(), str(erro)] + reler(modelo_id, detector_id)
        try:
            modelos_carregados[novo_id] = modelos.carregar_modelo_por_id(
                caminho_database, pasta_arquivos_de_modelos, arvore_dnit, novo_id)
            texto = f"Modelo {nome_modelo.strip()} cadastrado."
        except ValueError as erro:
            problemas_de_carga[novo_id] = str(erro)
            texto = f"Modelo {nome_modelo.strip()} cadastrado, mas não carregou. {erro}"
        return [None, None, texto] + reler(novo_id, detector_id)

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
        return [_descrever_detector(caminho_database, arvore_dnit, detector), escolhido,
                _botao_remover_detector(detector), OCULTO, OCULTO, aviso]

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
            return OCULTO, OCULTO, OCULTO, "Esse detector não existe mais."
        return OCULTO, VISIVEL, VISIVEL, f"Remover o detector {detector['nome']}?"

    def remover_detector(modelo_id, detector_id):
        """Confirmação da remoção do detector."""
        detector = _procurar_por_id(contrato_dados.detectores(caminho_database), detector_id)
        try:
            contrato_dados.remover_detector(caminho_database, detector_id)
        except ValueError as erro:
            return reler(modelo_id, detector_id, aviso_detector=str(erro))
        return reler(modelo_id, None,
                     aviso_detector=f"Detector {detector['nome']} removido.")

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
            return [nome, resolucao, limiar, maximo, str(erro)] + reler(modelo_escolhido, detector_id)
        return (["", "", "", "", f"Detector {nome.strip()} criado."]
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
                    lista_modelos = gr.Dataframe(value=[], headers=["Nome"],
                                                 label="Modelos cadastrados", interactive=False)
                    detalhe_modelo = gr.Markdown()
                    if gerenciar_modelos:
                        with gr.Row():
                            botao_remover_modelo = gr.Button("Remover", variant="stop", visible=False)
                            botao_confirmar_modelo = gr.Button("Confirmar remoção", variant="stop",
                                                               visible=False)
                            botao_cancelar_modelo = gr.Button("Cancelar", visible=False)
                        aviso_remocao_modelo = gr.Markdown()
                if gerenciar_modelos:
                    with gr.Column(scale=1):
                        gr.Markdown("### Cadastrar modelo")
                        arquivo = gr.File(label="Arquivo do modelo (.pt)", file_types=[".pt"],
                                          type="filepath")

                        @gr.render(inputs=classes_lidas)
                        def desenhar_correspondencia(nomes):
                            if not nomes:
                                return
                            gr.Markdown(f"**Classes encontradas no arquivo:** {len(nomes)}")
                            seletores = []
                            for nome_da_classe in nomes:
                                seletores.append(gr.Dropdown(opcoes_norma, value=None,
                                                             label=nome_da_classe))
                            nome_modelo = gr.Textbox(label="Nome do modelo", max_lines=1)
                            botao_salvar = gr.Button("Salvar modelo", variant="primary")
                            botao_salvar.click(salvar,
                                               inputs=[arquivo, classes_lidas, nome_modelo,
                                                       escolhido_modelo, escolhido_detector] + seletores,
                                               outputs=[arquivo, classes_lidas, aviso_cadastro] + tudo)

                        aviso_cadastro = gr.Markdown()

        with gr.Tab("Detectores"):
            with gr.Row():
                with gr.Column(scale=2):
                    lista_detectores = gr.Dataframe(value=[],
                                                    headers=["Nome", "Modelo", "Entrada", "Limiar", "Máx. det."],
                                                    label="Detectores cadastrados",
                                                    interactive=False)
                    detalhe_detector = gr.Markdown()
                    with gr.Row():
                        botao_remover_detector = gr.Button("Remover", variant="stop", visible=False)
                        botao_confirmar_detector = gr.Button("Confirmar remoção", variant="stop",
                                                             visible=False)
                        botao_cancelar_detector = gr.Button("Cancelar", visible=False)
                    aviso_remocao_detector = gr.Markdown()
                with gr.Column(scale=1):
                    gr.Markdown("### Criar detector")
                    nome = gr.Textbox(label="Nome do detector", max_lines=1)
                    modelo_do_detector = gr.Dropdown([], value=None, label="Modelo")
                    with gr.Row():
                        resolucao = gr.Textbox(label="Entrada (px)", max_lines=1, placeholder="em pixels")
                        limiar = gr.Textbox(label="Limiar", max_lines=1, placeholder="entre 0 e 1")
                        maximo = gr.Textbox(label="Máx. det.", max_lines=1, placeholder="a partir de 1")
                    botao_criar = gr.Button("Criar detector", variant="primary")
                    aviso_criacao = gr.Markdown()

    saidas_selecao_modelo = [detalhe_modelo, escolhido_modelo]
    if gerenciar_modelos:
        saidas_selecao_modelo.extend([botao_remover_modelo, botao_confirmar_modelo,
                                      botao_cancelar_modelo, aviso_remocao_modelo])
    saidas_selecao_detector = [detalhe_detector, escolhido_detector, botao_remover_detector,
                               botao_confirmar_detector, botao_cancelar_detector, aviso_remocao_detector]
    tudo = ([lista_modelos, ids_modelos] + saidas_selecao_modelo
            + [lista_detectores, ids_detectores] + saidas_selecao_detector + [modelo_do_detector])

    lista_modelos.select(clicar_modelo, inputs=ids_modelos, outputs=saidas_selecao_modelo)
    lista_detectores.select(clicar_detector, inputs=ids_detectores, outputs=saidas_selecao_detector)
    botao_criar.click(criar,
                      inputs=[nome, modelo_do_detector, resolucao, limiar, maximo,
                              escolhido_modelo, escolhido_detector],
                      outputs=[nome, resolucao, limiar, maximo, aviso_criacao] + tudo)
    botao_remover_detector.click(pedir_remocao_detector, inputs=escolhido_detector,
                                 outputs=[botao_remover_detector, botao_confirmar_detector,
                                          botao_cancelar_detector, aviso_remocao_detector])
    botao_confirmar_detector.click(remover_detector, inputs=[escolhido_modelo, escolhido_detector],
                                   outputs=tudo)
    botao_cancelar_detector.click(selecionar_detector, inputs=escolhido_detector,
                                  outputs=saidas_selecao_detector)

    if gerenciar_modelos:
        botao_remover_modelo.click(pedir_remocao_modelo, inputs=escolhido_modelo,
                                   outputs=[botao_remover_modelo, botao_confirmar_modelo,
                                            botao_cancelar_modelo, aviso_remocao_modelo])
        botao_confirmar_modelo.click(remover_modelo, inputs=[escolhido_modelo, escolhido_detector],
                                     outputs=tudo)
        botao_cancelar_modelo.click(selecionar_modelo, inputs=escolhido_modelo,
                                    outputs=saidas_selecao_modelo)
        arquivo.upload(ler_arquivo, inputs=arquivo, outputs=[classes_lidas, aviso_cadastro])
        arquivo.clear(esquecer_arquivo, outputs=[classes_lidas, aviso_cadastro])

    return reler, [escolhido_modelo, escolhido_detector], tudo
