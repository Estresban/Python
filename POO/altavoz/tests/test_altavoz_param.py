import pytest
from src.altavoz.altavoz import Altavoz # Ajusta esta importación según cómo se llame tu módulo



# ==========================================
# 1. PRUEBAS DE CREACIÓN
# ==========================================
def test_creacion_altavoz_correcta():
    altavoz = Altavoz("Salón", 40)
    assert altavoz.nombre == "Salón"
    assert altavoz.volumen == 40
    assert altavoz.estado == "Apagado"


def test_creacion_elimina_espacios_nombre():
    altavoz = Altavoz("   Cocina   ", 20)
    assert altavoz.nombre == "Cocina"


# ==========================================
# 2. PRUEBAS DE PROPIEDADES (Casos válidos)
# ==========================================
def test_modificar_nombre_valido():
    altavoz = Altavoz("Inicial", 30)
    altavoz.nombre = "  Dormitorio  "
    assert altavoz.nombre == "Dormitorio"


@pytest.mark.parametrize("volumen_valido",[0, 50, 100])
def test_modificar_volumen_valido(volumen_valido):
    altavoz = Altavoz("Estudio", 30)
    altavoz.volumen = volumen_valido
    assert altavoz.volumen == volumen_valido


def test_estado_no_se_puede_modificar_directamente():
    altavoz = Altavoz("Pasillo", 30)
    with pytest.raises(AttributeError):
        altavoz.estado = "Encendido"


# ==========================================
# 3. PRUEBAS DE COMPORTAMIENTO
# ==========================================
def test_encender_altavoz():
    altavoz = Altavoz("Jardín", 50)
    altavoz.encender()
    assert altavoz.estado == "Encendido"


def test_apagar_altavoz_encendido():
    altavoz = Altavoz("Jardín", 50)
    altavoz.encender()
    altavoz.apagar()
    assert altavoz.estado == "Apagado"


def test_idempotencia_encender_y_apagar():
    """Comprueba que llamar dos veces seguidas al mismo método mantiene el estado."""
    altavoz = Altavoz("Terraza", 25)
    altavoz.encender()
    altavoz.encender()
    assert altavoz.estado == "Encendido"

    altavoz.apagar()
    altavoz.apagar()
    assert altavoz.estado == "Apagado"


# ==========================================
# 4. PRUEBAS DE VALIDACIÓN Y ERRORES
# ==========================================
@pytest.mark.parametrize("nombre_invalido", ["", "   ", "\t\n"])
def test_nombre_vacio_o_espacios_lanza_value_error(nombre_invalido):
    with pytest.raises(ValueError):
        Altavoz(nombre_invalido, 30)


@pytest.mark.parametrize("nombre_no_str", [25, None, ["Salón"], 3.14])
def test_nombre_no_cadena_lanza_value_error(nombre_no_str):
    with pytest.raises(ValueError):
        Altavoz(nombre_no_str, 30)


@pytest.mark.parametrize("volumen_fuera_rango", [-1, -50, 101, 200])
def test_volumen_fuera_de_rango_lanza_value_error(volumen_fuera_rango):
    with pytest.raises(ValueError):
        Altavoz("Baño", volumen_fuera_rango)


@pytest.mark.parametrize("volumen_tipo_invalido", ["50", True, False, 45.5, None])
def test_volumen_tipo_incorrecto_lanza_value_error(volumen_tipo_invalido):
    with pytest.raises(ValueError):
        Altavoz("Baño", volumen_tipo_invalido)


def test_validacion_en_setters_al_modificar():
    """Comprueba que las validaciones también se aplican al modificar, no solo en __init__."""
    altavoz = Altavoz("Oficina", 50)

    with pytest.raises(ValueError):
        altavoz.nombre = "   "

    with pytest.raises(ValueError):
        altavoz.volumen = 150

    with pytest.raises(ValueError):
        altavoz.volumen = False
