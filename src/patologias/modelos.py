"""Cadastro, carga e uso dos modelos, com conferência do arquivo de modelo antes do uso."""

import hashlib
import shutil
import time
from pathlib import Path
import cv2
from ultralytics import YOLO
from database import contrato_dados
from patologias import catalogo


def sha256(caminho_arquivo):
    with open(caminho_arquivo, "rb") as arquivo:
        return hashlib.file_digest(arquivo, "sha256").hexdigest()


def _lista(nomes):
    if not nomes:
        return "nenhuma"
    return ", ".join(nomes)


def abrir_modelo(caminho_arquivo):
    try:
        return YOLO(str(caminho_arquivo))
    except Exception as erro:
        raise ValueError(f"O arquivo de modelo não abriu, {erro}.") from erro


def ler_classes(modelo_ultralytics):
    """Classes que o modelo declara, do número para o nome."""
    classes_no_modelo = {}
    for numero, nome in modelo_ultralytics.names.items():
        classes_no_modelo[int(numero)] = str(nome)
    return classes_no_modelo


def traduzir_classes(arvore_dnit, classes_no_modelo, correspondencia_classes):
    """Liga o número de cada classe do modelo à patologia da norma, pelo nome."""
    if sorted(classes_no_modelo.values()) != sorted(correspondencia_classes):
        sobram = sorted(set(classes_no_modelo.values()) - set(correspondencia_classes))
        faltam = sorted(set(correspondencia_classes) - set(classes_no_modelo.values()))
        raise ValueError("As classes do modelo não são as do cadastro (só no modelo, "
                         f"{_lista(sobram)}; só no cadastro, {_lista(faltam)}).")
    patologias_inexistentes = set()
    for identificador_dnit in correspondencia_classes.values():
        if identificador_dnit is not None and not catalogo.existe(arvore_dnit, identificador_dnit):
            patologias_inexistentes.add(identificador_dnit)
    if patologias_inexistentes:
        raise ValueError("Patologia que não existe mais no catálogo da norma, "
                         f"{', '.join(sorted(patologias_inexistentes))}.")
    traducao_classes = {}
    for numero, nome in classes_no_modelo.items():
        if correspondencia_classes[nome] is not None:
            traducao_classes[numero] = correspondencia_classes[nome]
    return traducao_classes


def cadastrar_arquivo_de_modelo(caminho_database,
                                pasta_arquivos_de_modelos,
                                arvore_dnit,
                                caminho_arquivo,
                                nome,
                                correspondencia_classes):
    """Copia o arquivo do modelo para a pasta da plataforma e grava a "ficha"."""
    nome = nome.strip()
    classes_no_modelo = ler_classes(abrir_modelo(caminho_arquivo))
    traduzir_classes(arvore_dnit, classes_no_modelo, correspondencia_classes)
    pasta = Path(pasta_arquivos_de_modelos)
    nome_do_arquivo = f"{nome}.pt"
    destino = pasta / nome_do_arquivo
    if destino.resolve().parent != pasta.resolve():
        raise ValueError(f"Nome de modelo inválido para arquivo, {nome}.")
    if destino.exists():
        raise ValueError(f"Já existe um arquivo de modelo com o nome {nome}.")
    pasta.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(caminho_arquivo, destino)
    try:
        return contrato_dados.cadastrar_modelo(caminho_database,
                                                arvore_dnit,
                                                nome,
                                                nome_do_arquivo,
                                                sha256(destino),
                                                correspondencia_classes)
    except Exception:
        destino.unlink()
        raise


def remover_arquivo_de_modelo(caminho_database, pasta_arquivos_de_modelos, modelo_id):
    """Apaga a ficha do modelo e depois a cópia do arquivo de modelo."""
    nome_do_arquivo = None
    for cadastro_do_modelo in contrato_dados.modelos(caminho_database):
        if cadastro_do_modelo["id"] == modelo_id:
            nome_do_arquivo = cadastro_do_modelo["caminho_arquivo_de_modelo"]
    contrato_dados.remover_modelo(caminho_database, modelo_id)
    (Path(pasta_arquivos_de_modelos) / nome_do_arquivo).unlink(missing_ok=True)


def carregar_modelo(pasta_arquivos_de_modelos,
                    arvore_dnit,
                    cadastro_do_modelo,
                    correspondencia_classes):
    """Confere e carrega um modelo cadastrado."""
    arquivo_de_modelo = (Path(pasta_arquivos_de_modelos)
                         / cadastro_do_modelo["caminho_arquivo_de_modelo"])
    if not arquivo_de_modelo.is_file():
        raise ValueError(f"Arquivo de modelo não encontrado em {arquivo_de_modelo}.")
    if sha256(arquivo_de_modelo) != cadastro_do_modelo["sha256"]:
        raise ValueError("O arquivo de modelo mudou desde o cadastro (SHA-256 diferente).")
    modelo_ultralytics = abrir_modelo(arquivo_de_modelo)
    traducao_classes = traduzir_classes(arvore_dnit, ler_classes(modelo_ultralytics),
                                        correspondencia_classes)
    return dict(modelo_ultralytics=modelo_ultralytics, traducao_classes=traducao_classes,
                classes=sorted(traducao_classes),
                passo=int(modelo_ultralytics.model.stride.max()))


def carregar_modelos_cadastrados(caminho_database, pasta_arquivos_de_modelos, arvore_dnit):
    """Carrega os modelos cadastrados, e devolve os carregados e os problemas, por id."""
    carregados = {}
    problemas = {}
    for cadastro_do_modelo in contrato_dados.modelos(caminho_database):
        modelo_id = cadastro_do_modelo["id"]
        correspondencia_classes = contrato_dados.classes(caminho_database, modelo_id)
        try:
            carregados[modelo_id] = carregar_modelo(pasta_arquivos_de_modelos,
                                                    arvore_dnit,
                                                    cadastro_do_modelo,
                                                    correspondencia_classes)
        except ValueError as erro:
            problemas[modelo_id] = str(erro)
    return carregados, problemas


def criar_detector(caminho_database, modelo_carregado, nome, modelo_id, resolucao_entrada, limiar_confianca, max_deteccoes):
    """Grava um detector, conferindo a resolução contra o passo do modelo."""
    passo = modelo_carregado["passo"]
    if isinstance(resolucao_entrada, int) and resolucao_entrada % passo:
        raise ValueError(f"A resolução de entrada precisa ser múltiplo de {passo}, o passo deste modelo.")
    return contrato_dados.criar_detector(caminho_database,
                                            nome,
                                            modelo_id,
                                            resolucao_entrada,
                                            limiar_confianca,
                                            max_deteccoes)


def _confianca(deteccao):
    return deteccao["confianca"]


def detectar(arvore_dnit, modelo_carregado, detector, imagem_rgb):
    """Roda o detector numa imagem e devolve as detecções e o tempo em milissegundos."""
    imagem_bgr = cv2.cvtColor(imagem_rgb, cv2.COLOR_RGB2BGR)
    inicio = time.perf_counter()
    resultado = modelo_carregado["modelo_ultralytics"].predict(imagem_bgr,
                                                                imgsz=detector["resolucao_entrada"],
                                                                conf=detector["limiar_confianca"],
                                                                max_det=detector["max_deteccoes"],
                                                                classes=modelo_carregado["classes"],
                                                                verbose=False)[0]
    tempo_ms = (time.perf_counter() - inicio) * 1000
    deteccoes = []
    for caixa in resultado.boxes:
        identificador_dnit = modelo_carregado["traducao_classes"][int(caixa.cls)]
        xyxy = []
        for valor in caixa.xyxy[0].tolist():
            xyxy.append(int(round(valor)))
        deteccoes.append(dict(xyxy=xyxy,
                                identificador_dnit=identificador_dnit,
                                classe=catalogo.rotulo(arvore_dnit, identificador_dnit),
                                confianca=float(caixa.conf)))
    deteccoes.sort(key=_confianca, reverse=True)
    return deteccoes, tempo_ms
