"""Tela de Análise, a imagem entra e saem as bounding boxes e a tabela."""

import gradio as gr
import numpy as np
from PIL import Image, ImageOps

from database import contrato_dados
from patologias import modelos
from visual import desenho

SEM_DETECTOR = "Nenhum detector cadastrado."


def ler_imagem(caminho_arquivo):
    """Abre a imagem enviada, aplica a orientação gravada pela câmera e devolve em RGB."""
    with Image.open(caminho_arquivo) as original:
        orientada = ImageOps.exif_transpose(original)
        return np.array(orientada.convert("RGB"))


def _opcoes_detectores(detectores):
    """Opções do seletor, o nome que aparece e o id que a análise usa."""
    opcoes = []
    for detector in detectores:
        opcoes.append((detector["nome"], detector["id"]))
    return opcoes


def _procurar_detector(detectores, detector_id):
    """O detector com esse id, ou None."""
    for detector in detectores:
        if detector["id"] == detector_id:
            return detector
    return None


def _ler_detector(caminho_database, detector_id):
    """O detector com esse id, lido do database agora, ou None."""
    return _procurar_detector(contrato_dados.detectores(caminho_database), detector_id)


def _descrever_detector(detector):
    """Modelo usado pelo detector e a configuração de inferência dele."""
    if detector is None:
        return SEM_DETECTOR
    limiar = str(detector["limiar_confianca"]).replace(".", ",")
    return (f"**Modelo:** {detector['modelo_nome']}  \n"
            f"entrada {detector['resolucao_entrada']} px · limiar {limiar} · "
            f"máx. {detector['max_deteccoes']} detecções")


def _resumir_analise(deteccoes, tempo_ms):
    """Quantas detecções e quanto tempo a detecção levou."""
    quantidade = len(deteccoes)
    if quantidade == 1:
        texto = "1 detecção"
    else:
        texto = f"{quantidade} detecções"
    return f"{texto} em {tempo_ms:.0f} ms"


def montar(caminho_database, arvore_dnit, modelos_carregados, problemas_de_carga, cores):
    """Monta a tela de Análise e devolve a função que relê os detectores, com entradas e saídas."""
    detectores = contrato_dados.detectores(caminho_database)
    opcoes = _opcoes_detectores(detectores)
    inicial = None
    if detectores:
        inicial = detectores[0]["id"]

    def mostrar_descricao(detector_id):
        return _descrever_detector(_ler_detector(caminho_database, detector_id))

    def atualizar(detector_id):
        detectores_agora = contrato_dados.detectores(caminho_database)
        escolhido = _procurar_detector(detectores_agora, detector_id)
        if escolhido is None and detectores_agora:
            escolhido = detectores_agora[0]
        valor = None
        if escolhido is not None:
            valor = escolhido["id"]
        opcoes_agora = _opcoes_detectores(detectores_agora)
        seletor_novo = gr.update(choices=opcoes_agora, value=valor, interactive=bool(opcoes_agora))
        return seletor_novo, _descrever_detector(escolhido)

    def analisar(caminho_arquivo, detector_id):
        if not caminho_arquivo:
            raise gr.Error("Envie uma imagem antes de analisar.")
        detector = _ler_detector(caminho_database, detector_id)
        if detector is None:
            raise gr.Error(SEM_DETECTOR)
        modelo_id = detector["modelo_id"]
        if modelo_id in problemas_de_carga:
            raise gr.Error(f"O modelo {detector['modelo_nome']} não carregou. {problemas_de_carga[modelo_id]}")
        if modelo_id not in modelos_carregados:
            raise gr.Error(f"O modelo {detector['modelo_nome']} não foi carregado ao iniciar a plataforma.")
        imagem = ler_imagem(caminho_arquivo)
        deteccoes, tempo_ms = modelos.detectar(arvore_dnit, modelos_carregados[modelo_id], detector, imagem)
        linhas = []
        for deteccao in deteccoes:
            linhas.append([deteccao["classe"], desenho.porcentagem(deteccao["confianca"])])
        return (desenho.desenhar(imagem, deteccoes, cores), linhas, _resumir_analise(deteccoes, tempo_ms))

    with gr.Row():
        with gr.Column():
            entrada = gr.Image(label="Imagem do pavimento", type="filepath", image_mode=None)
            seletor = gr.Dropdown(opcoes, value=inicial, label="Detector", interactive=bool(opcoes))
            descricao = gr.Markdown(_descrever_detector(_procurar_detector(detectores, inicial)))
            botao = gr.Button("Analisar", variant="primary")
        with gr.Column():
            saida = gr.Image(label="Patologias encontradas")
            resumo = gr.Markdown()
            tabela = gr.Dataframe(headers=["Patologia", "Confiança"], label="Detecções", interactive=False)

    seletor.change(mostrar_descricao, inputs=seletor, outputs=descricao)
    botao.click(analisar, inputs=[entrada, seletor], outputs=[saida, tabela, resumo])
    return atualizar, [seletor], [seletor, descricao]
