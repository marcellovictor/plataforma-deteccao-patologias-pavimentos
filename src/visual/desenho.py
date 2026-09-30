"""Desenho das bounding boxes sobre a imagem analisada."""

import cv2
from patologias import catalogo

# Paleta Okabe-Ito, distinguível nas formas comuns de daltonismo.
CORES_FIXAS = {
    "trinca_longitudinal": (230, 159, 0),
    "trinca_transversal": (86, 180, 233),
    "trinca_jacare": (0, 158, 115),
    "panela": (213, 94, 0),
}

PALETA_DERIVADA = [
    (240, 228, 66),
    (0, 114, 178),
    (204, 121, 167),
]

COR_FALLBACK = (204, 121, 167)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
FONTE = cv2.FONT_HERSHEY_SIMPLEX


def tabela_de_cores(arvore_dnit):
    """Cor de cada patologia do catálogo, fixa nas quatro principais e derivada nas outras."""
    cores = {}
    derivadas = 0
    for identificador, _profundidade in catalogo.em_ordem(arvore_dnit):
        if identificador in CORES_FIXAS:
            cores[identificador] = CORES_FIXAS[identificador]
        else:
            cores[identificador] = PALETA_DERIVADA[derivadas % len(PALETA_DERIVADA)]
            derivadas = derivadas + 1
    return cores


def desenhar(imagem, deteccoes, cores):
    """Imagem com uma bounding box desenhada em cada detecção."""
    saida = imagem.copy()
    lado = max(saida.shape[:2])
    espessura = max(2, lado // 400)
    fonte = max(0.5, lado / 1500)
    for deteccao in deteccoes:
        x1, y1, x2, y2 = deteccao["xyxy"]
        cor = cores.get(deteccao["identificador_dnit"], COR_FALLBACK)
        cv2.rectangle(saida, (x1, y1), (x2, y2), cor, espessura)
        texto = f'{deteccao["classe"]} {porcentagem(deteccao["confianca"])}'
        (largura, altura), _ = cv2.getTextSize(texto, FONTE, fonte, espessura)
        base = linha_de_base(y1, altura)
        cv2.rectangle(saida, (x1 - espessura // 2, base - altura - 6), (x1 + largura + 8, base + 4), cor, -1)
        cv2.putText(saida, texto, (x1 + 4, base), FONTE, fonte, tinta(cor), espessura, cv2.LINE_AA)
    return saida


def porcentagem(confianca):
    return f"{confianca * 100:.1f}%".replace(".", ",")


def linha_de_base(y1, altura_do_texto):
    """Onde o texto se apoia, acima da bounding box, ou dentro dela se não houver espaço."""
    if y1 - altura_do_texto - 10 >= 0:
        return y1 - 4
    return y1 + altura_do_texto + 6


def tinta(cor):
    """Cor da letra que fica legível sobre a cor de fundo, pela luminância da WCAG."""
    vermelho, verde, azul = cor
    luminancia = (0.2126 * vermelho + 0.7152 * verde + 0.0722 * azul) / 255
    if luminancia > 0.5:
        return PRETO
    return BRANCO
