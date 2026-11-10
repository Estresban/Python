from ejemplo_pytest.operaciones import sumar

def test_sumar_dos_numeros():
    resultado = sumar(3, 5)

    assert resultado == 8