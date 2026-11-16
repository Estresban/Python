###########################################################
###########################################################
# PRUEBA 1   Comprobacion de puertos 
###########################################################
###########################################################

'''
from dvrip import DVRIPCam

# Prueba con tu contraseña o déjala vacía ("") si no tiene clave
cam = DVRIPCam("192.168.1.23", user="xxx", password="xxx")

if cam.login():
    print("Conexión exitosa al puerto 34567.")
    print("Configuración ONVIF actual:", cam.get_info("NetWork.Onvif"))
    print("Configuración RTSP actual:", cam.get_info("NetWork.RTSP"))
    cam.close()
else:
    print("No se pudo iniciar sesión. Revisa el usuario y la contraseña.")

import socket

ip = "192.168.1.2"
for puerto in (554, 8899, 80, 34567):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    abierto = s.connect_ex((ip, puerto)) == 0
    print(f"Puerto {puerto}: {'ABIERTO' if abierto else 'CERRADO'}")
    s.close()
'''
###########################################################
###########################################################
# PRUEBA 2  Programa de visualizacion de video
###########################################################
###########################################################

'''
import subprocess
import threading
import cv2
import numpy as np
from dvrip import DVRIPCam

IP_GARAJE = "192.168.1.2"
USUARIO = "xxx"
CLAVE = "xxx"  

# 1. Conectar al puerto 34567
cam = DVRIPCam(IP_GARAJE, user=USUARIO, password=CLAVE)
if not cam.login():
    print("Error al iniciar sesión en la cámara del garaje.")
    exit()

print("Conectado al puerto 34567. Iniciando flujo de video...")

# 2. Configurar FFmpeg para convertir H264/H265 crudo a frames BGR para OpenCV
ancho, alto = 640, 360

comando_ffmpeg = (
    "ffmpeg",
    "-i", "pipe:0",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{ancho}x{alto}",
    "-an", "-sn",
    "pipe:1"
)

proceso_ffmpeg = subprocess.Popen(
    comando_ffmpeg,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

# 3. Hilo que ejecuta start_monitor (método oficial de python-dvr)
def alimentar_video():

    def al_recibir_paquete(frame, meta, user):

        if frame is None or not meta:
            return

        tipo = meta.get("type")

        # Solo enviar vídeo, nunca audio
        if tipo in ("h264", "h265", "mpeg4"):

            try:
                proceso_ffmpeg.stdin.write(frame)
                proceso_ffmpeg.stdin.flush()
                print("Paquete recibido:", meta, "Tamaño:", len(frame) if frame else 0)

            except (BrokenPipeError, OSError) as e:
                print("Error enviando vídeo a FFmpeg:", e)

        elif tipo == "g711a":
            pass

    try:
        cam.start_monitor(al_recibir_paquete, None)

    except Exception as e:
        print("Error recibiendo vídeo de la cámara:", e)

hilo = threading.Thread(target=alimentar_video, daemon=True)
hilo.start()

# 4. Bucle principal de OpenCV
tamano_frame = ancho * alto * 3

try:
    while True:
        raw_frame = proceso_ffmpeg.stdout.read(tamano_frame)
        if len(raw_frame) != tamano_frame:
            continue

        imagen = np.frombuffer(raw_frame, dtype=np.uint8).reshape((alto, ancho, 3))
        cv2.imshow("Camara Garaje (Puerto 34567)", imagen)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('w'):
            cam.ptz("DirectionUp")
        elif tecla == ord('s'):
            cam.ptz("DirectionDown")
        elif tecla == ord('a'):
            cam.ptz("DirectionLeft")
        elif tecla == ord('d'):
            cam.ptz("DirectionRight")
finally:
    cam.stop_monitor()
    cam.close()
    proceso_ffmpeg.terminate()
    cv2.destroyAllWindows()

'''
###########################################################
###########################################################
# PRUEBA 3 Sacar informacion 
###########################################################
###########################################################
'''
from dvrip import DVRIPCam
import json
#("192.168.1.2", user="xxx", password="xxx")
IP = "192.168.1.2"
USUARIO = "xxx"
CLAVE = "xxx"

cam = DVRIPCam(IP, user=USUARIO, password=CLAVE)

print("Métodos disponibles relacionados con configuración:")
for nombre in dir(cam):
    if any(p in nombre.lower() for p in ("config", "info", "rtsp", "monitor", "system")):
        print(nombre)

if cam.login():
    print("\n--- RTSP ---")
    print(json.dumps(
        cam.get_info("NetWork.RTSP"),
        indent=4
    ))

    print("\n--- ONVIF ---")
    print(json.dumps(
        cam.get_info("NetWork.Onvif"),
        indent=4
    ))

    print("\n--- INFORMACIÓN DEL SISTEMA ---")
    print(json.dumps(
        cam.get_info("General"),
        indent=4
    ))

    cam.close()
else:
    print("Error de conexión DVRIP")
    '''
###########################################################
###########################################################  
# PRUEBA 4 Sacar metodos de configuracion de XM80
###########################################################
###########################################################
'''
import inspect

for nombre in [
    "start_monitor",
    "stop_monitor",
    "set_info",
    "get_system_info",
    "get_system_capabilities",
    "get_camera_info",
    "get_encode_info"
]:
    metodo = getattr(cam, nombre, None)

    if metodo:
        print("\n" + "=" * 50)
        print("MÉTODO:", nombre)

        try:
            print("Firma:", inspect.signature(metodo))
            print(inspect.getsource(metodo))
        except Exception as e:
            print("No se pudo obtener el código:", e)
            
'''
###########################################################
###########################################################
# PRUEBA 5 Esperar paquetes de video para analizar
###########################################################
###########################################################


'''
import threading
import time
from dvrip import DVRIPCam
import json


#("192.168.1.2", user="xxx", password="xxx")
IP = "192.168.1.2"
USUARIO = "xxx"
CLAVE = "xxx"

cam = DVRIPCam(IP, user=USUARIO, password=CLAVE)

if not cam.login():
    print("Error al iniciar sesión en la cámara del garaje.")
    exit()
'''
'''
paquetes = []

def recibir_video(frame, meta, user):
    paquetes.append((frame, meta))

    if len(paquetes) <= 5:
        print(f"\nPaquete {len(paquetes)}")
        print("Tamaño:", len(frame) if frame else 0)
        print("Metadatos:", meta)

def iniciar_monitor():
    try:
        resultado = cam.start_monitor(recibir_video)
        print("Resultado de start_monitor:", resultado)
    except Exception as e:
        print("Error en start_monitor:", repr(e))

hilo = threading.Thread(target=iniciar_monitor, daemon=True)
hilo.start()

print("Esperando vídeo durante 10 segundos...")
time.sleep(10)


#print("=== INFORMACIÓN DE CÁMARA ===")
#print(json.dumps(cam.get_camera_info(), indent=4, ensure_ascii=False))

#print("\n=== CONFIGURACIÓN DE CODIFICACIÓN ===")
#print(json.dumps(cam.get_encode_info(), indent=4, ensure_ascii=False))

#print("\n=== CAPACIDADES DEL SISTEMA ===")
#print(json.dumps(cam.get_system_capabilities(), indent=4, ensure_ascii=False))


cam.stop_monitor()
hilo.join(timeout=3)

print("\nTotal de paquetes recibidos:", len(paquetes))
'''


'''
for comando in [
    "OPMonitor",
    "NetWork.RTSP",
    "Simplify.Encode",
    "Camera"
]:
    print("\n==========", comando, "==========")
    try:
        resultado = cam.get_info(comando)
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    except Exception as e:
        print("Error:", repr(e))
        
'''
    
#########################################################
#########################################################
# prueba de codigo
#########################################################
#########################################################



import subprocess
import threading
import cv2
import numpy as np
from dvrip import DVRIPCam
import queue
import time

IP_GARAJE = "192.168.1.2"
USUARIO = "xxx"
CLAVE = "xxx"

ANCHO = 640
ALTO = 360

cam = DVRIPCam(IP_GARAJE, user=USUARIO, password=CLAVE)

if not cam.login():
    raise SystemExit("No se pudo iniciar sesión en la cámara")

print("Conectado a la cámara .22")

cola_video = queue.Queue()

comando = (
    "ffmpeg",
    "-loglevel", "error",
    "-f", "hevc",
    "-i", "pipe:0",
    "-an",
    "-vf", f"scale={ANCHO}:{ALTO}",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "pipe:1"
)

# Guardamos los errores de FFmpeg para poder diagnosticarlos
log_ffmpeg = open("ffmpeg_error.log", "w")

proceso_ffmpeg = subprocess.Popen(
    comando,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=log_ffmpeg,
    bufsize=0
)
'''
def recibir_video(frame, meta, user):
    if frame is None or not meta:
        return

    if meta.get("frame") in ("I", "P"):
        cola_video.put(bytes(frame))
'''
def recibir_video(frame, meta, user):
    if frame is None or not meta:
        return

    if meta.get("frame") in ("I", "P"):
        cola_video.put(bytes(frame))

    elif meta.get("type") == "g711a":
        print(
            "AUDIO:",
            meta.get("type"),
            "| Tamaño:",
            len(frame)
        )

def alimentar_ffmpeg():
    while True:
        paquete = cola_video.get()

        if paquete is None:
            break

        try:
            proceso_ffmpeg.stdin.write(paquete)
            proceso_ffmpeg.stdin.flush()
        except (BrokenPipeError, OSError):
            print("FFmpeg ha dejado de recibir datos")
            break


hilo_ffmpeg = threading.Thread(
    target=alimentar_ffmpeg,
    daemon=True
)
hilo_ffmpeg.start()

try:
    hilo_cam = threading.Thread(
        target=lambda: cam.start_monitor(recibir_video, None),
        daemon=True
    )
    hilo_cam.start()

    bytes_frame = ANCHO * ALTO * 3

    print("Esperando imagen de la cámara...")


    buffer = bytearray()

    while True:

        if proceso_ffmpeg.poll() is not None:
            print("FFmpeg se ha cerrado")
            break

        datos = proceso_ffmpeg.stdout.read(65536)

        if not datos:
            print("FFmpeg no entrega más datos")
            break

        buffer.extend(datos)

        while len(buffer) >= bytes_frame:
            datos_frame = bytes(buffer[:bytes_frame])
            del buffer[:bytes_frame]

            imagen = np.frombuffer(
                datos_frame, dtype=np.uint8
            ).reshape((ALTO, ANCHO, 3))

            cv2.imshow(
                "Camara .22 - Prueba individual",
                imagen
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                raise KeyboardInterrupt

finally:
    try:
        cam.stop_monitor()
    except Exception:
        pass

    cola_video.put(None)

    cam.close()

    proceso_ffmpeg.terminate()
    proceso_ffmpeg.wait()

    log_ffmpeg.close()

    cv2.destroyAllWindows()
