import gradio as gr
from patologias import catalogo
from telas import informacoes
from visual import desenho

TITULO = "Plataforma para detecção e classificação de patologias em pavimentos asfálticos"


# TODO depois ajustar dado mockado
DETECTORES_MOCK = ["cenario base", "vencedor do ORDDC 2024"]


def montar():
    """Monta a página da plataforma e a devolve, sem subir servidor."""
    arvore_dnit = catalogo.carregar()
    cores = desenho.tabela_de_cores(arvore_dnit)

    # TODO depois ajustar dado mockado
    def analisar_mock(imagem, detector):
        if imagem is None:
            raise gr.Error("Envie uma imagem antes de analisar.")
        deteccoes = [
            dict(xyxy=(80, 60, 420, 300), identificador_dnit="trinca_longitudinal",
                 classe="Trinca longitudinal", confianca=0.99),
            dict(xyxy=(300, 380, 700, 620), identificador_dnit="trinca_jacare",
                 classe="Trinca jacaré", confianca=0.67),
            dict(xyxy=(120, 500, 260, 640), identificador_dnit="panela",
                 classe="Panela", confianca=0.42),
        ]
        linhas = []
        for deteccao in deteccoes:
            linhas.append([deteccao["classe"], desenho.porcentagem(deteccao["confianca"])])
        return desenho.desenhar(imagem, deteccoes, cores), linhas

    with gr.Blocks(title=TITULO) as pagina:
        gr.Markdown(f"# {TITULO}")
        with gr.Tabs():
            with gr.Tab("Análise"):
                with gr.Row():
                    with gr.Column():
                        entrada = gr.Image(label="Imagem do pavimento", type="numpy")
                        detector = gr.Dropdown(DETECTORES_MOCK,
                                               value=DETECTORES_MOCK[0],
                                               label="Detector")
                        analisar = gr.Button("Analisar", variant="primary")
                    with gr.Column():
                        saida = gr.Image(label="Patologias encontradas")
                        tabela = gr.Dataframe(headers=["Patologia", "Confiança"],
                                              label="Detecções", interactive=False)
                analisar.click(analisar_mock, inputs=[entrada, detector],
                               outputs=[saida, tabela])
            with gr.Tab("Informações"):
                informacoes.montar(arvore_dnit)
            with gr.Tab("Configurações"):
                gr.Markdown("Modelos cadastrados e detectores.")
    return pagina

if __name__ == "__main__":
    montar().launch()