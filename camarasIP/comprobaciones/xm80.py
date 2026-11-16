
from dvrip import DVRIPCam
import json
from getpass import getpass

IP = "192.168.1.3"
USUARIO = "xxx"

#CLAVE = getpass("Contraseña de la cámara: ")
CLAVE ="xxxx"
cam = DVRIPCam(IP, user=USUARIO, password=CLAVE)

consultas = [
    "SystemInfo",
    "General",
    "SystemFunction",
    "NetWork",
    "NetWork.NetCommon",
    "NetWork.NetDHCP",
    "NetWork.RTSP",
    "NetWork.Onvif",
    "Simplify.Encode",
    "Camera"
]

try:
    print("\nConectando con XM80...")

    if not cam.login():
        print("Error de autenticación.")
        raise SystemExit

    print("Conexión DVRIP correcta.")

    resultados = {}

    for comando in consultas:
        print("\nConsultando:", comando)

        try:
            datos = cam.get_info(comando)
            resultados[comando] = datos

            print(json.dumps(
                datos,
                indent=2,
                ensure_ascii=False,
                default=str
            ))

        except Exception as e:
            print("No disponible:", e)
            resultados[comando] = str(e)

    with open(
        "resultado_xm80_3.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            resultados,
            archivo,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    print("\n================================")
    print("CONSULTA FINALIZADA")
    print("Archivo creado: resultado_xm80.json")
    print("================================")

finally:
    cam.close()

# ur2uh8
'''

try:
    import audioop
    print("audioop disponible")
except ImportError:
    print("audioop no disponible")
'''