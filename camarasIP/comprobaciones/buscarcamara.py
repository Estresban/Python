import socket
import concurrent.futures

def escanear_camara_garaje(ip):
    # 8899 es el puerto ONVIF de tu error; 554 es el puerto de video RTSP
    puertos = [8899, 554, 80, 8000, 34567, 37777]
    abiertos = []
    for p in puertos:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.4)
        if s.connect_ex((ip, p)) == 0:
            abiertos.append(p)
        s.close()
    return (ip, abiertos) if abiertos else None

print("Buscando la cámara del garaje en 192.168.1.x...")
ips = [f"192.168.1.{i}" for i in range(1, 255)]

with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
    for res in executor.map(escanear_camara_garaje, ips):
        if res:
            ip, puertos = res
            if 8899 in puertos or 554 in puertos:
                print(f"[¡ENCONTRADA!] Nueva posible IP: {ip} -> Puertos: {puertos}")
            else:
                print(f"[Otro dispositivo] IP: {ip} -> Puertos: {puertos}")
