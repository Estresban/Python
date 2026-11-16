
import socket
import webbrowser
import urllib.request

IP = "192.168.1.22"

PUERTOS = {
    80: "HTTP",
    443: "HTTPS",
    554: "RTSP",
    8899: "ONVIF",
    8999: "ONVIF alternativo",
    34567: "DVRIP / XM",
    8000: "Alternativo",
    8080: "HTTP alternativo",
    81: "HTTP alternativo"
}

abiertos = []

print("=" * 45)
print("       ESCANER CAMARA XM80 - ICSEE")
print("=" * 45)
print("IP:", IP)
print()

for puerto, servicio in PUERTOS.items():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    resultado = s.connect_ex((IP, puerto))
    s.close()

    if resultado == 0:
        print(f"[ABIERTO] {puerto} - {servicio}")
        abiertos.append(puerto)
    else:
        print(f"[CERRADO] {puerto} - {servicio}")

print("\n" + "=" * 45)
print("       BUSCANDO MENU WEB")
print("=" * 45)

for puerto in abiertos:

    if puerto not in (80, 443, 8080, 81):
        continue

    protocolo = "https" if puerto == 443 else "http"
    url = f"{protocolo}://{IP}:{puerto}/"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=4) as respuesta:
            print("\nInterfaz web encontrada:")
            print("URL:", url)
            print("Estado HTTP:", respuesta.status)

            webbrowser.open(url)
            break

    except Exception as e:
        print(f"No se pudo abrir {url}: {e}")

else:
    print("\nNo se ha encontrado una interfaz web accesible.")

print("\nESCANEO FINALIZADO")
input("Pulsa ENTER para salir...")
