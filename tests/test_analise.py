"""Teste da leitura da imagem enviada na tela de Análise."""

from PIL import Image
from telas import analise


def test_ler_imagem_aplica_orientacao_da_camera(tmp_path):
    caminho = tmp_path / "foto.jpg"
    exif = Image.Exif()
    exif[0x0112] = 6    # marca de orientação: girar 90 graus para ficar em pé
    Image.new("RGB", (40, 20), (255, 0, 0)).save(caminho, exif=exif)
    lida = analise.ler_imagem(caminho)
    assert lida.shape == (40, 20, 3)
