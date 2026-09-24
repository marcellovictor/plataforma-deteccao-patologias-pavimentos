"""Testes do catálogo da norma."""

from patologias import catalogo


def test_carrega_a_arvore_inteira():
    cat = catalogo.carregar()
    assert len(cat["patologias"]) == 37
    assert cat["raizes"] == ["fenda", "outros_defeitos"]
    assert cat["fonte"].startswith("DNIT 005/2003-TER")


def test_codigos_da_folha_sao_o_proprio():
    cat = catalogo.carregar()
    assert catalogo.codigos(cat, "panela") == ["P"]


def test_codigos_de_um_no_acima_vem_das_folhas():
    cat = catalogo.carregar()
    assert catalogo.codigos(cat, "trinca_jacare") == ["J", "JE"]
    assert catalogo.codigos(cat, "trinca_longitudinal") == ["TLC", "TLL"]
    assert catalogo.codigos(cat, "fenda") == [
        "FI", "TTC", "TTL", "TLC", "TLL", "J", "JE", "TRR", "TB", "TBE"]


def test_a_norma_tem_21_codigos():
    cat = catalogo.carregar()
    total = 0
    for raiz in cat["raizes"]:
        total += len(catalogo.codigos(cat, raiz))
    assert total == 21


def test_rotulo_prefere_o_nome_de_exibicao():
    cat = catalogo.carregar()
    assert catalogo.rotulo(cat, "trinca_jacare") == "Trinca jacaré"
    assert catalogo.rotulo(cat, "fissura") == "Fissuras"


def test_em_ordem_passa_por_todos_com_o_pai_antes():
    cat = catalogo.carregar()
    ordem = list(catalogo.em_ordem(cat))
    assert len(ordem) == 37
    assert ordem[0] == ("fenda", 0)
    assert dict(ordem)["trinca_transversal_curta"] == 4


def test_existe_so_para_quem_esta_no_catalogo():
    cat = catalogo.carregar()
    assert catalogo.existe(cat, "panela")
    assert not catalogo.existe(cat, "buraco")