'''Ejercicio 16. Acceso a una aplicación
Solicita:

Usuario
Contraseña
Los datos correctos serán:

Usuario: admin
Contraseña: python123
Si ambos son correctos:

Acceso permitido
En caso contrario:

Usuario o contraseña incorrectos
'''

usuario = input("Introduce el usuario: ")
contrasena = input("Introduce la contraseña: ") 

if usuario == "admin" and contrasena == "python123":
    print("Acceso permitido")
else:
    print("Usuario o contraseña incorrectos")
    