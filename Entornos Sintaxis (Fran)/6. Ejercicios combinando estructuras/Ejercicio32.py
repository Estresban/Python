'''Ejercicio 32. Contraseña con tres intentos
Solicita usuario y contraseña.

El usuario tendrá un máximo de tres intentos.

Si los datos son correctos:

Acceso permitido
Si falla tres veces:

Cuenta bloqueada
Utiliza un while.'''

usuario_correcto = "admin"
contrasena_correcta = "1234"
intentos = 0
while intentos < 3:
    usuario = input("Usuario: ")
    contrasena = input("Contraseña: ")
    if usuario == usuario_correcto and contrasena == contrasena_correcta:
        print("Acceso permitido")
        break
    else:
        intentos += 1
        print(f"Intento {intentos} fallido")
else:
    print("Cuenta bloqueada")
