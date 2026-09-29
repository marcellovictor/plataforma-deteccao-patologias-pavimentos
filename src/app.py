import gradio as gr

TITULO = "Plataforma para detecção e classificação de patologias em pavimentos asfálticos"


# TODO depois ajustar dado mockado
DETECTORES_MOCK = ["cenario base", "vencedor do ORDDC 2024"]


# TODO depois ajustar dado mockado
def analisar_mock(imagem, detector):
    if imagem is None:
        raise gr.Error("Envie uma imagem antes de analisar.")
    deteccoes = [
        ["Trinca longitudinal", "99%"],
        ["Trinca jacaré", "67%"],
        ["Panela", "42%"],
    ]
    return imagem, deteccoes

def montar():
    """Monta a página da plataforma e a devolve, sem subir servidor."""
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
                gr.Markdown("Patologias da norma DNIT 005/2003-TER que a plataforma reconhece.")
            with gr.Tab("Configurações"):
                gr.Markdown("Modelos cadastrados e detectores.")
    return pagina

if __name__ == "__main__":
    montar().launch()