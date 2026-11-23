import pytest
from src.altavoz.altavoz import Altavoz


# Crear un altavoz con nombre ""
def test_negat01_nombre_vacio():
    with pytest.raises(ValueError):
        Altavoz("", 50)
       
# Crear un altavoz con nombre "   "
def test_negat02_nombre_espacios():
    with pytest.raises(ValueError):
        Altavoz("   ", 50)

# Crear un altavoz con nombre 25
def test_negat03_nombre_no_string():
    with pytest.raises(ValueError):
        Altavoz(25, 50)


# Crear un altavoz con volumen -1
def test_negat04_volumen_negativo():
    with pytest.raises(ValueError):
        Altavoz("Salón", -1)
        

# Crear un altavoz con volumen 101
def test_negat05_volumen_mayor_100():
    with pytest.raises(ValueError):
        Altavoz("Salón", 101)


# Asignar altavoz.volumen = 25.5
def test_negat06_volumen_decimal():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(ValueError):
        altavoz.volumen = 25.5
        

# Asignar altavoz.volumen = "alto"
def test_negat07_volumen_texto():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(ValueError):
        altavoz.volumen = "alto"
        

# Asignar altavoz.estado = "encendido"
def test_negat08_estado_solo_lectura():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(AttributeError):
        altavoz.estado = "encendido"


'''
        
# Crear un altavoz con nombre ""
def test_negat01_nombre_vacio():
    with pytest.raises(ValueError, match="El nombre no puede estar vacio"):
        Altavoz("", 50)


# Crear un altavoz con nombre "   "
def test_negat02_nombre_espacios():
    with pytest.raises(ValueError, match="El nombre no puede estar vacio"):
        Altavoz("   ", 50)


# Crear un altavoz con nombre 25
def test_negat03_nombre_no_string():
    with pytest.raises(ValueError, match="El nombre debe ser cadena de texto"):
        Altavoz(25, 50)


# Crear un altavoz con volumen -1
def test_negat04_volumen_negativo():
    with pytest.raises(ValueError, match="El volumen debe estar entre 0 y 100"):
        Altavoz("Salón", -1)


# Crear un altavoz con volumen 101
def test_negat05_volumen_mayor_100():
    with pytest.raises(ValueError, match="El volumen debe estar entre 0 y 100"):
        Altavoz("Salón", 101)


# Asignar altavoz.volumen = 25.5
def test_negat06_volumen_decimal():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(ValueError, match="El volumen debe ser un numero entero"):
        altavoz.volumen = 25.5


# Asignar altavoz.volumen = "alto"
def test_negat07_volumen_texto():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(ValueError, match="El volumen debe ser un numero entero"):
        altavoz.volumen = "alto"


# Asignar altavoz.estado = "encendido"
def test_negat08_estado_solo_lectura():
    altavoz = Altavoz("Salón", 50)
    with pytest.raises(AttributeError):
        altavoz.estado = "encendido"
        
'''