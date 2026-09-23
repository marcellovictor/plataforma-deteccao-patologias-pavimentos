import gradio as gr

TITULO = "Plataforma para detecção e classificação de patologias em pavimentos asfálticos"


def montar():
    with gr.Blocks(title=TITULO) as pagina:
        gr.Markdown(f"# {TITULO}")
    return pagina

if __name__ == "__main__":
    montar().launch()