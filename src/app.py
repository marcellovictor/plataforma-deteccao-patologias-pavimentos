import argparse
from pathlib import Path
import gradio as gr
from database import contrato_dados
from patologias import catalogo, modelos
from telas import analise, configuracoes, informacoes
from visual import desenho, estilo

TITULO = "Plataforma para detecção e classificação de patologias em pavimentos asfálticos"
ROTULO_DO_CABECALHO = "Plataforma"
TITULO_DO_CABECALHO = "Detecção e classificação de patologias em pavimentos asfálticos"
RAIZ = Path(__file__).parents[1]
CAMINHO_DATABASE = RAIZ / "plataforma.db"
PASTA_ARQUIVOS_DE_MODELOS = RAIZ / "arquivos_de_modelos"


def ler_argumentos():
    """Lê da linha de comando o database, a pasta dos arquivos de modelos e se o gerenciamento de modelos fica ligado."""
    leitor = argparse.ArgumentParser(description=TITULO)
    leitor.add_argument("--database", type=Path, default=CAMINHO_DATABASE,
                        help="arquivo do database, padrão plataforma.db na raiz do repositório")
    leitor.add_argument("--arquivos-de-modelos", type=Path, default=PASTA_ARQUIVOS_DE_MODELOS,
                        help="pasta dos arquivos de modelos, padrão arquivos_de_modelos/ na raiz do repositório")
    leitor.add_argument("--gerenciar-modelos", action="store_true",
                        help="liga o cadastro e a remoção de modelos na tela de Configurações")
    return leitor.parse_args()


def _visibilidade_das_telas(indice):
    """Visibilidade das três telas, em que só a de número indice aparece."""
    visibilidades = []
    for numero in range(3):
        visibilidades.append(gr.update(visible=numero == indice))
    return visibilidades


def mostrar_analise():
    """Mostra a tela de Análise e esconde as outras duas."""
    return _visibilidade_das_telas(0)


def mostrar_informacoes():
    """Mostra a tela de Informações e esconde as outras duas."""
    return _visibilidade_das_telas(1)


def mostrar_configuracoes():
    """Mostra a tela de Configurações e esconde as outras duas."""
    return _visibilidade_das_telas(2)


def _botao_voltar():
    """Botão com cara de link, no topo de uma tela, que leva de volta à Análise."""
    with gr.Row(elem_classes="pav-volta"):
        return gr.Button("← Voltar à análise", size="sm", scale=0, min_width=150)


def montar(caminho_database, pasta_arquivos_de_modelos, gerenciar_modelos=False):
    """Monta a página da plataforma e a devolve, sem subir servidor."""
    arvore_dnit = catalogo.carregar()
    cores = desenho.tabela_de_cores(arvore_dnit)
    caminho_database = contrato_dados.abrir(caminho_database)
    modelos_carregados, problemas_de_carga = modelos.carregar_modelos_cadastrados(caminho_database, pasta_arquivos_de_modelos, arvore_dnit)
    for modelo_id, problema in problemas_de_carga.items():
        print(f"O modelo de id {modelo_id} não carregou. {problema}")
    if gerenciar_modelos:
        print("Cadastro e remoção de modelos ligados na tela de Configurações.")

    with gr.Blocks(title=TITULO) as pagina:
        with gr.Row(elem_classes="pav-cabecalho"):
            botao_analise = gr.Button("Análise", size="sm", scale=0, min_width=110,
                                      icon=estilo.PASTA_ICONES / "scan-search.svg")
            estilo.bloco(f'{estilo.rotulo(ROTULO_DO_CABECALHO)}'
                         f'<h1 class="pav-titulo">{TITULO_DO_CABECALHO}</h1>',
                         scale=1, min_width=240)
            botao_informacoes = gr.Button("Informações", size="sm", scale=0, min_width=130,
                                          icon=estilo.PASTA_ICONES / "informacoes.svg")
            botao_configuracoes = gr.Button("Configurações", size="sm", scale=0, min_width=140,
                                            icon=estilo.PASTA_ICONES / "configuracoes.svg")

        with gr.Column(visible=True, elem_classes="pav-tela") as tela_analise:
            atualizar_analise, entradas_analise, saidas_analise = analise.montar(
                caminho_database, arvore_dnit, modelos_carregados, problemas_de_carga, cores)
        with gr.Column(visible=False, elem_classes="pav-tela") as tela_informacoes:
            voltar_de_informacoes = _botao_voltar()
            informacoes.montar(arvore_dnit)
        with gr.Column(visible=False, elem_classes="pav-tela") as tela_configuracoes:
            voltar_de_configuracoes = _botao_voltar()
            atualizar_configuracoes, entradas_configuracoes, saidas_configuracoes = configuracoes.montar(
                caminho_database, pasta_arquivos_de_modelos, arvore_dnit, modelos_carregados, problemas_de_carga, cores, gerenciar_modelos)
        telas = [tela_analise, tela_informacoes, tela_configuracoes]

        botao_analise.click(mostrar_analise, outputs=telas).then(atualizar_analise,
                                                                inputs=entradas_analise,
                                                                outputs=saidas_analise)
        botao_informacoes.click(mostrar_informacoes, outputs=telas)
        botao_configuracoes.click(mostrar_configuracoes, outputs=telas).then(atualizar_configuracoes,
                                                                            inputs=entradas_configuracoes,
                                                                            outputs=saidas_configuracoes)
        voltar_de_informacoes.click(mostrar_analise, outputs=telas).then(atualizar_analise,
                                                                        inputs=entradas_analise,
                                                                        outputs=saidas_analise)
        voltar_de_configuracoes.click(mostrar_analise, outputs=telas).then(atualizar_analise,
                                                                            inputs=entradas_analise,
                                                                            outputs=saidas_analise)
        pagina.load(atualizar_analise,
                    inputs=entradas_analise,
                    outputs=saidas_analise)
    return pagina


if __name__ == "__main__":
    argumentos = ler_argumentos()
    montar(argumentos.database, argumentos.arquivos_de_modelos, argumentos.gerenciar_modelos).launch(theme=estilo.TEMA, css=estilo.CSS, js=estilo.FORCAR_MODO_CLARO)
