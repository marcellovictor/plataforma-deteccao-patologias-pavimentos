import numpy
from patologias import catalogo
from visual import desenho


def imagem_preta(altura=400, largura=400):
    return numpy.zeros((altura, largura, 3), dtype=numpy.uint8)


def uma_deteccao():
    return dict(xyxy=(100, 100, 300, 300),
                identificador_dnit="trinca_longitudinal",
                classe="Trinca longitudinal",
                confianca=0.9)


def cores():
    return desenho.tabela_de_cores(catalogo.carregar())


def test_nao_altera_a_imagem_recebida():
    original = imagem_preta()
    desenho.desenhar(original, [uma_deteccao()], cores())
    assert original.max() == 0


def test_sem_deteccoes_nao_desenha_nada():
    saida = desenho.desenhar(imagem_preta(), [], cores())
    assert saida.max() == 0


def test_desenha_a_borda_de_cima_na_cor_da_patologia():
    saida = desenho.desenhar(imagem_preta(), [uma_deteccao()], cores())
    assert tuple(saida[100, 200]) == desenho.CORES_FIXAS["trinca_longitudinal"]


def test_toda_patologia_do_catalogo_tem_cor():
    arvore_dnit = catalogo.carregar()
    tabela = desenho.tabela_de_cores(arvore_dnit)
    assert set(tabela) == set(arvore_dnit["patologias"])


def test_patologias_diferentes_fora_das_fixas_recebem_cores_diferentes():
    tabela = desenho.tabela_de_cores(catalogo.carregar())
    derivadas = []
    for identificador, cor in tabela.items():
        if identificador not in desenho.CORES_FIXAS:
            derivadas.append(cor)
    assert len(set(derivadas[:3])) == 3


def test_confianca_vira_porcentagem_com_uma_casa():
    assert desenho.porcentagem(0.984) == "98,4%"


def test_porcentagem_usa_virgula_decimal():
    assert "," in desenho.porcentagem(0.5)


def test_rotulo_fica_acima_da_bounding_box_quando_ha_espaco():
    assert desenho.linha_de_base(100, 20) < 100


def test_rotulo_desce_para_dentro_quando_encosta_no_topo():
    assert desenho.linha_de_base(2, 20) > 2


def test_fundo_claro_recebe_letra_escura():
    assert desenho.tinta(desenho.CORES_FIXAS["trinca_longitudinal"]) == desenho.PRETO


def test_fundo_escuro_recebe_letra_clara():
    assert desenho.tinta((0, 114, 178)) == desenho.BRANCO


def test_escreve_o_rotulo_acima_da_bounding_box():
    saida = desenho.desenhar(imagem_preta(), [uma_deteccao()], cores())
    faixa = saida[70:99, 100:340]
    assert faixa.max() > 0


def test_o_rotulo_nao_tapa_o_interior_da_bounding_box():
    saida = desenho.desenhar(imagem_preta(), [uma_deteccao()], cores())
    assert saida[200, 200].max() == 0
