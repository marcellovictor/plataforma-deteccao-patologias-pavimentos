import argparse
from pathlib import Path
import gradio as gr
from database import contrato_dados
from patologias import catalogo, modelos
from telas import analise, informacoes, configuracoes
from visual import desenho

TITULO = "Plataforma para detecção e classificação de patologias em pavimentos asfálticos"
RAIZ = Path(__file__).parents[1]
CAMINHO_DATABASE = RAIZ / "plataforma.db"
PASTA_ARQUIVOS_DE_MODELOS = RAIZ / "arquivos_de_modelos"


def ler_argumentos():
    """Lê da linha de comando onde ficam o database e a pasta dos arquivos de modelos."""
    leitor = argparse.ArgumentParser(description=TITULO)
    leitor.add_argument("--database", type=Path, default=CAMINHO_DATABASE,
                        help="arquivo do database, padrão plataforma.db na raiz do repositório")
    leitor.add_argument("--arquivos-de-modelos", type=Path, default=PASTA_ARQUIVOS_DE_MODELOS,
                        help="pasta dos arquivos de modelos, padrão arquivos_de_modelos/ "
                             "na raiz do repositório")
    return leitor.parse_args()


def montar(caminho_database, pasta_arquivos_de_modelos):
    """Monta a página da plataforma e a devolve, sem subir servidor."""
    arvore_dnit = catalogo.carregar()
    cores = desenho.tabela_de_cores(arvore_dnit)
    caminho_database = contrato_dados.abrir(caminho_database)
    modelos_carregados, problemas_de_carga = modelos.carregar_modelos_cadastrados(caminho_database, pasta_arquivos_de_modelos, arvore_dnit)
    for modelo_id, problema in problemas_de_carga.items():
        print(f"O modelo de id {modelo_id} não carregou. {problema}")

    with gr.Blocks(title=TITULO) as pagina:
        gr.Markdown(f"# {TITULO}")
        with gr.Tabs():
            with gr.Tab("Análise") as aba_analise:
                atualizar_analise, entradas_analise, saidas_analise = analise.montar(
                    caminho_database, arvore_dnit, modelos_carregados, problemas_de_carga, cores)
            with gr.Tab("Informações"):
                informacoes.montar(arvore_dnit)
            with gr.Tab("Configurações") as aba_configuracoes:
                atualizar_configuracoes, entradas_configuracoes, saidas_configuracoes = configuracoes.montar(
                    caminho_database, arvore_dnit, modelos_carregados)
        aba_analise.select(atualizar_analise, inputs=entradas_analise, outputs=saidas_analise)
        aba_configuracoes.select(atualizar_configuracoes, inputs=entradas_configuracoes,
                                 outputs=saidas_configuracoes)
        pagina.load(atualizar_analise, inputs=entradas_analise, outputs=saidas_analise)
        pagina.load(atualizar_configuracoes, inputs=entradas_configuracoes,
                    outputs=saidas_configuracoes)
    return pagina


if __name__ == "__main__":
    argumentos = ler_argumentos()
    montar(argumentos.database, argumentos.arquivos_de_modelos).launch()
