import numpy
import pytest
from ultralytics import YOLO
from database import contrato_dados
from patologias import catalogo
from patologias import modelos


def arvore():
    return catalogo.carregar()


def modelo_de_teste(pasta):
    caminho = pasta / "modelo_de_teste.pt"
    YOLO("yolov8n.yaml").save(str(caminho))
    return caminho


def correspondencia_de_teste():
    # O modelo gerado da planta declara 80 classes, de "0" a "79".
    correspondencia_classes = {}
    for numero in range(80):
        correspondencia_classes[str(numero)] = None
    correspondencia_classes["0"] = "trinca_longitudinal"
    correspondencia_classes["1"] = "panela"
    return correspondencia_classes


def ficha_de_teste(nome_do_arquivo, impressao_digital):
    return dict(id=1, nome="teste", caminho_arquivo_de_modelo=nome_do_arquivo, sha256=impressao_digital)


def test_traduz_o_numero_da_classe_pelo_nome():
    classes_no_modelo = {0: "D40", 1: "D00"}
    correspondencia_classes = {"D00": "trinca_longitudinal", "D40": "panela"}
    traducao_classes = modelos.traduzir_classes(arvore(), classes_no_modelo, correspondencia_classes)
    assert traducao_classes == {0: "panela", 1: "trinca_longitudinal"}


def test_classe_ignorada_fica_fora_da_traducao():
    classes_no_modelo = {0: "D00", 1: "Repair"}
    correspondencia_classes = {"D00": "trinca_longitudinal", "Repair": None}
    traducao_classes = modelos.traduzir_classes(arvore(), classes_no_modelo, correspondencia_classes)
    assert traducao_classes == {0: "trinca_longitudinal"}


def test_recusa_classes_diferentes_das_do_cadastro():
    classes_no_modelo = {0: "D00", 1: "D40"}
    correspondencia_classes = {"D00": "trinca_longitudinal", "D20": None}
    with pytest.raises(ValueError, match="só no modelo, D40; só no cadastro, D20"):
        modelos.traduzir_classes(arvore(), classes_no_modelo, correspondencia_classes)


def test_recusa_no_que_nao_existe_na_norma():
    classes_no_modelo = {0: "D00"}
    correspondencia_classes = {"D00": "no_inventado"}
    with pytest.raises(ValueError, match="no_inventado"):
        modelos.traduzir_classes(arvore(), classes_no_modelo, correspondencia_classes)


def test_recusa_arquivo_de_modelo_que_nao_existe(tmp_path):
    cadastro_do_modelo = ficha_de_teste("nao_existe.pt", "qualquer")
    with pytest.raises(ValueError, match="não encontrado"):
        modelos.carregar_modelo(tmp_path, arvore(), cadastro_do_modelo, {})


def test_recusa_arquivo_de_modelo_alterado_depois_do_cadastro(tmp_path):
    arquivo_de_modelo = tmp_path / "modelo.pt"
    arquivo_de_modelo.write_bytes(b"conteudo no dia do cadastro")
    cadastro_do_modelo = ficha_de_teste("modelo.pt", modelos.sha256(arquivo_de_modelo))
    arquivo_de_modelo.write_bytes(b"conteudo trocado depois")
    with pytest.raises(ValueError, match="mudou desde o cadastro"):
        modelos.carregar_modelo(tmp_path, arvore(), cadastro_do_modelo, {})


def test_recusa_arquivo_de_modelo_que_nao_abre(tmp_path):
    arquivo_de_modelo = tmp_path / "modelo.pt"
    arquivo_de_modelo.write_bytes(b"isto nao e um modelo")
    cadastro_do_modelo = ficha_de_teste("modelo.pt", modelos.sha256(arquivo_de_modelo))
    with pytest.raises(ValueError, match="não abriu"):
        modelos.carregar_modelo(tmp_path, arvore(), cadastro_do_modelo, {})


def test_cadastro_copia_o_arquivo_e_grava_a_ficha(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    enviado = modelo_de_teste(tmp_path)
    modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "teste", correspondencia_de_teste())
    ficha = contrato_dados.modelos(caminho_database)[0]
    assert ficha["caminho_arquivo_de_modelo"] == "teste.pt"
    assert ficha["sha256"] == modelos.sha256(enviado)
    assert modelos.sha256(pasta / "teste.pt") == modelos.sha256(enviado)


def test_cadastro_recusa_nome_que_ja_existe(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    enviado = modelo_de_teste(tmp_path)
    modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "teste", correspondencia_de_teste())
    with pytest.raises(ValueError, match="Já existe"):
        modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "teste", correspondencia_de_teste())


def test_cadastro_recusado_nao_deixa_arquivo_na_pasta(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    enviado = modelo_de_teste(tmp_path)
    with pytest.raises(ValueError):
        modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "", correspondencia_de_teste())
    assert list(pasta.iterdir()) == []


def test_carga_de_ponta_a_ponta(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database,
                                                    pasta,
                                                    arvore(),
                                                    modelo_de_teste(tmp_path),
                                                    "teste",
                                                    correspondencia_de_teste())
    carregados, problemas = modelos.carregar_modelos_cadastrados(caminho_database, pasta, arvore())
    assert problemas == {}
    assert carregados[modelo_id]["traducao_classes"] == {0: "trinca_longitudinal", 1: "panela"}
    assert carregados[modelo_id]["passo"] == 32


def test_modelo_com_arquivo_apagado_nao_impede_os_outros(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    enviado = modelo_de_teste(tmp_path)
    id_apagado = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "apagado", correspondencia_de_teste())
    id_inteiro = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), enviado, "inteiro", correspondencia_de_teste())
    (pasta / "apagado.pt").unlink()
    carregados, problemas = modelos.carregar_modelos_cadastrados(caminho_database, pasta, arvore())
    assert list(carregados) == [id_inteiro]
    assert "não encontrado" in problemas[id_apagado]


def test_criar_detector_recusa_resolucao_fora_do_passo(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    with pytest.raises(ValueError, match="múltiplo de 32"):
        modelos.criar_detector(caminho_database, dict(passo=32), "teste", 1, 100, 0.25, 300)


def test_detectar_devolve_so_classes_nao_ignoradas_em_ordem(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database,
                                                    pasta,
                                                    arvore(),
                                                    modelo_de_teste(tmp_path),
                                                    "teste",
                                                    correspondencia_de_teste())
    carregados, _ = modelos.carregar_modelos_cadastrados(caminho_database, pasta, arvore())
    detector = dict(resolucao_entrada=64, limiar_confianca=0.0, max_deteccoes=5)
    imagem = numpy.zeros((64, 64, 3), dtype=numpy.uint8)
    deteccoes, tempo_ms = modelos.detectar(arvore(), carregados[modelo_id], detector, imagem)
    assert len(deteccoes) <= 5
    assert tempo_ms >= 0
    confiancas = []
    for deteccao in deteccoes:
        assert deteccao["identificador_dnit"] in ("trinca_longitudinal", "panela")
        confiancas.append(deteccao["confianca"])
    assert confiancas == sorted(confiancas, reverse=True)


def test_remocao_apaga_a_ficha_e_o_arquivo(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), modelo_de_teste(tmp_path), "teste", correspondencia_de_teste())
    modelos.remover_arquivo_de_modelo(caminho_database, pasta, modelo_id)
    assert contrato_dados.modelos(caminho_database) == []
    assert not (pasta / "teste.pt").exists()


def test_remocao_recusada_deixa_o_arquivo(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), modelo_de_teste(tmp_path), "teste", correspondencia_de_teste())
    contrato_dados.criar_detector(caminho_database, "usa o teste", modelo_id, 640, 0.25, 300)
    with pytest.raises(ValueError, match="usa o teste"):
        modelos.remover_arquivo_de_modelo(caminho_database, pasta, modelo_id)
    assert (pasta / "teste.pt").exists()


def test_remocao_com_arquivo_ja_apagado_tira_a_ficha(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), modelo_de_teste(tmp_path), "teste", correspondencia_de_teste())
    (pasta / "teste.pt").unlink()
    modelos.remover_arquivo_de_modelo(caminho_database, pasta, modelo_id)
    assert contrato_dados.modelos(caminho_database) == []


def test_carga_por_id_devolve_o_modelo_carregado(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    modelo_id = modelos.cadastrar_arquivo_de_modelo(caminho_database, pasta, arvore(), modelo_de_teste(tmp_path), "teste", correspondencia_de_teste())
    modelo_carregado = modelos.carregar_modelo_por_id(caminho_database, pasta, arvore(), modelo_id)
    assert modelo_carregado["traducao_classes"] == {0: "trinca_longitudinal", 1: "panela"}
    assert modelo_carregado["passo"] == 32


def test_carga_por_id_recusa_id_inexistente(tmp_path):
    caminho_database = contrato_dados.abrir(tmp_path / "teste.db")
    pasta = tmp_path / "arquivos_de_modelos"
    with pytest.raises(ValueError, match="Não existe modelo cadastrado com id 99"):
        modelos.carregar_modelo_por_id(caminho_database, pasta, arvore(), 99)
