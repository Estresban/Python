import pytest
from baraja import Carta


def test_str_de_carta():
    assert str(Carta(5, 'oros')) == '5 de oros'


def test_repr_de_carta():
    assert repr(Carta(5, 'oros')) == "Carta(5, 'oros')"


def test_cartas_iguales():
    assert Carta(5, 'oros') == Carta(5, 'oros')
    assert Carta(5, 'oros') != Carta(5, 'copas')


def test_cartas_en_set_sin_duplicados():
    assert len({Carta(5, 'oros'), Carta(5, 'oros')}) == 1


def test_orden_por_valor():
    cartas = [Carta(9, 'oros'), Carta(2, 'copas'), Carta(5, 'bastos')]
    assert [c.valor for c in sorted(cartas)] == [2, 5, 9]


def test_valor_fuera_de_rango():
    with pytest.raises(ValueError):
        Carta(13, 'oros')


'''def test_mazo_nuevo_tiene_48_cartas():
    assert len(Mazo()) == 48


def test_robar_quita_una_carta():
    mazo = Mazo()
    carta = mazo.robar()
    assert len(mazo) == 47
    assert carta not in mazo


def test_in_funciona_con_el_mazo():
    assert Carta(1, 'oros') in Mazo()


def test_se_puede_recorrer_el_mazo():
    assert sum(1 for _ in Mazo()) == 48


def test_robar_de_mazo_vacio():
    mazo = Mazo()
    for _ in range(48):
        mazo.robar()
    with pytest.raises(ValueError):
        mazo.robar()'''