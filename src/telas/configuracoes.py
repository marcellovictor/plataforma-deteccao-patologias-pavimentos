"""Tela de Configurações, os detectores e, com a opção, os modelos."""

import gradio as gr

from database import contrato_dados
from patologias import catalogo, modelos

OCULTO = gr.update(visible=False)
VISIVEL = gr.update(visible=True)
SEM_DETECTOR = "Nenhum detector cadastrado."


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


def _botao_remover(detector):
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


def montar(caminho_database, arvore_dnit, modelos_carregados):
    """Monta a tela de Configurações e devolve a função que a relê, com entradas e saídas."""

    def selecionar(detector_id, aviso=""):
        """Detalhe, id escolhido, os três botões e o aviso. Sem id válido, o primeiro da lista."""
        detectores = contrato_dados.detectores(caminho_database)
        detector = _procurar_por_id(detectores, detector_id)
        if detector is None and detectores:
            detector = detectores[0]
        escolhido = None
        if detector is not None:
            escolhido = detector["id"]
        return [_descrever_detector(caminho_database, arvore_dnit, detector), escolhido, _botao_remover(detector), OCULTO, OCULTO, aviso]

    def reler(detector_id, aviso=""):
        """Tudo da subaba, relido do database."""
        detectores = contrato_dados.detectores(caminho_database)
        opcoes = _opcoes_modelos(caminho_database, modelos_carregados)
        return ([_linhas_detectores(detectores), _ids(detectores)]
                + selecionar(detector_id, aviso)
                + [gr.update(choices=opcoes)])

    def clicar(ids, evento: gr.SelectData):
        """Clicar em uma linha da tabela."""
        return selecionar(ids[evento.index[0]])

    def pedir_remocao(detector_id):
        """Primeiro clique em Remover, troca o botão pela confirmação."""
        detector = _procurar_por_id(contrato_dados.detectores(caminho_database), detector_id)
        if detector is None:
            return OCULTO, OCULTO, OCULTO, "Esse detector não existe mais."
        return OCULTO, VISIVEL, VISIVEL, f"Remover o detector {detector['nome']}?"

    def remover(detector_id):
        """Confirmação da remoção."""
        detector = _procurar_por_id(contrato_dados.detectores(caminho_database), detector_id)
        try:
            contrato_dados.remover_detector(caminho_database, detector_id)
        except ValueError as erro:
            return reler(detector_id, str(erro))
        return reler(None, f"Detector {detector['nome']} removido.)

    def criar(nome, modelo_id, resolucao, limiar, maximo, detector_id):
        """Botão Criar detector."""
        try:
            if modelo_id is None:
                raise ValueError("Escolha o modelo do detector.")
            novo_id = modelos.criar_detector(caminho_database,
                                             modelos_carregados[modelo_id],
                                             nome,
                                             modelo_id,
                                             _inteiro_digitado(resolucao, "Entrada"),
                                             _limiar_digitado(limiar),
                                             _inteiro_digitado(maximo, "Máximo de detecções"))
        except ValueError as erro:
            return [nome, resolucao, limiar, maximo, str(erro)] + reler(detector_id)
        return ["", "", "", "", f"Detector {nome.strip()} criado."] + reler(novo_id)

    ids_detectores = gr.State([])
    escolhido = gr.State(None)

    with gr.Tabs():
        with gr.Tab("Detectores"):
            with gr.Row():
                with gr.Column(scale=2):
                    lista = gr.Dataframe(value=[],
                                         headers=["Nome", "Modelo", "Entrada", "Limiar", "Máx. det."],
                                         label="Detectores cadastrados",
                                         interactive=False)
                    detalhe = gr.Markdown()
                    with gr.Row():
                        botao_remover = gr.Button("Remover", variant="stop", visible=False)
                        botao_confirmar = gr.Button("Confirmar remoção", variant="stop", visible=False)
                        botao_cancelar = gr.Button("Cancelar", visible=False)
                    aviso_remocao = gr.Markdown()
                with gr.Column(scale=1):
                    gr.Markdown("### Criar detector")
                    nome = gr.Textbox(label="Nome do detector", max_lines=1)
                    modelo = gr.Dropdown([], value=None, label="Modelo")
                    with gr.Row():
                        resolucao = gr.Textbox(label="Entrada (px)", max_lines=1, placeholder="em pixels")
                        limiar = gr.Textbox(label="Limiar", max_lines=1, placeholder="entre 0 e 1")
                        maximo = gr.Textbox(label="Máx. det.", max_lines=1, placeholder="a partir de 1")
                    botao_criar = gr.Button("Criar detector", variant="primary")
                    aviso_criacao = gr.Markdown()

    saidas_selecao = [detalhe, escolhido, botao_remover, botao_confirmar, botao_cancelar, aviso_remocao]
    tudo = [lista, ids_detectores] + saidas_selecao + [modelo]

    lista.select(clicar, inputs=ids_detectores, outputs=saidas_selecao)
    botao_criar.click(criar,
                      inputs=[nome, modelo, resolucao, limiar, maximo, escolhido],
                      outputs=[nome, resolucao, limiar, maximo, aviso_criacao] + tudo)
    botao_remover.click(pedir_remocao, inputs=escolhido,
                        outputs=[botao_remover, botao_confirmar, botao_cancelar, aviso_remocao])
    botao_confirmar.click(remover, inputs=escolhido, outputs=tudo)
    botao_cancelar.click(selecionar, inputs=escolhido, outputs=saidas_selecao)
    return reler, [escolhido], tudo
