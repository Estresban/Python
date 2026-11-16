'''from dvrip import DVRIPCam

camaras = {
    "Camara_2": ("192.168.1.2", "xxx"),   # Pon la clave de cada una si tienen
    "Camara_3": ("192.168.1.3", "xxx"),
    "Camara_4": ("192.168.1.4", "xxx"),
    "Garaje_5": ("192.168.1.5", "xxx")
}

for nombre, (ip, clave) in camaras.items():
    cam = DVRIPCam(ip, user="admin", password=clave)
    if cam.login():
        info = cam.get_info("SystemInfo")
        print(f"=== {nombre} ({ip}) ===")
        print("  HardWare :", info.get("HardWare"))
        print("  SoftWare :", info.get("SoftWareVersion"))
        print("  BuildTime:", info.get("BuildTime"))
        cam.close()
    else:
        print(f"=== {nombre} ({ip}) -> Error de login ===")'''
        
from dvrip import DVRIPCam

# Usa las mismas credenciales con las que sacaste los archivos JSON
camaras = {
    "": ("xxxx", "xxx", "xxx"),
    "xxx": ("xxxx", "xxx", "xxx"),
    "xxx": ("xxxx", "xxx", "xxx"),
    "xxx": ("xxxx", "xxx", "xxx")  # Pon aquí la clave que usaste para sacar el 80.json
}

for nombre, (ip, usuario, clave) in camaras.items():
    cam = DVRIPCam(ip, user=usuario, password=clave)
    if cam.login():
        info = cam.get_info("SystemInfo")
        print(f"=== {nombre} ({ip}) ===")
        if info:
            print("  HardWare :", info.get("HardWare"))
            print("  SoftWare :", info.get("SoftWareVersion"))
            print("  BuildTime:", info.get("BuildTime"))
        else:
            print("  Login OK, pero SystemInfo devolvió vacío (Ret: 607).")
        cam.close()
    else:
        print(f"=== {nombre} ({ip}) -> Error de login con usuario '{usuario}' ===")

