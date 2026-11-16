import socket
import subprocess
import re
import concurrent.futures

def obtener_red_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    finally:
        s.close()
    return ".".join(ip_local.split(".")[:-1]) + "."

def obtener_mac_arp(ip):
    try:
        salida = subprocess.check_output(["arp", "-a", ip], text=True, stderr=subprocess.DEVNULL)
        coincidencia = re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", salida)
        if coincidencia:
            return coincidencia.group(0).replace("-", ":").upper()
    except Exception:
        pass
    return "Desconocida"

def escanear_todo(ip):
    # Ampliamos la búsqueda a puertos comunes de cámaras (RTSP, ONVIF, HTTP, RTMP, privados)
    puertos_ampliados = [80, 443, 554, 1935, 5000, 8000, 8080, 8554, 8899, 9000, 34567]
    abiertos = []
    for p in puertos_ampliados:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        if s.connect_ex((ip, p)) == 0:
            abiertos.append(p)
        s.close()
    return (ip, abiertos) if abiertos else None

def buscar_dispositivos_red():
    prefijo = obtener_red_local()
    print(f"Buscando TODOS los dispositivos activos en {prefijo}0/24...\n")
    ips = [f"{prefijo}{i}" for i in range(1, 255)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        for res in executor.map(escanear_todo, ips):
            if res:
                ip, puertos = res
                mac = obtener_mac_arp(ip)
                # Las cámaras Xiongmai/iCSee suelen empezar por MAC 00:12:35 o tener el puerto 34567 abierto
                marca_pista = " <-- ¡Posible cámara iCSee/XM!" if (34567 in puertos or mac.startswith("00:12:35")) else ""
                print(f"IP: {ip:<14} | MAC: {mac:<17} | Puertos: {puertos}{marca_pista}")

if __name__ == "__main__":
    buscar_dispositivos_red()
