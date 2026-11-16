'''
import urllib.request
import re

IP = "192.168.1.22"
URL = f"http://{IP}/"

try:
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode("utf-8", errors="ignore")

        print("Estado:", r.status)
        print("Servidor:", r.headers.get("Server"))
        print("Tipo:", r.headers.get("Content-Type"))

        titulo = re.findall(
            r"<title[^>]*>(.*?)</title>",
            html,
            re.I | re.S
        )

        print("\nTITULO:")
        print(titulo)

        print("\nARCHIVOS JAVASCRIPT:")
        for js in re.findall(
            r'<script[^>]+src=["\']([^"\']+)',
            html,
            re.I
        ):
            print(js)

        print("\nENLACES:")
        for enlace in re.findall(
            r'href=["\']([^"\']+)',
            html,
            re.I
        ):
            print(enlace)

        print("\nCONTENIDO HTML (primeros 3000 caracteres):")
        print(html[:3000])

except Exception as e:
    print("Error:", e)


##########################################################



import urllib.request
import re

BASE = "http://192.168.1.22/"

archivos = [
    "pluginVersion.js",
    "js/main.js"
]

for archivo in archivos:
    print("\n" + "=" * 55)
    print("ANALIZANDO:", archivo)
    print("=" * 55)

    try:
        req = urllib.request.Request(
            BASE + archivo,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            contenido = r.read().decode(
                "utf-8", errors="ignore"
            )

        print("Archivo encontrado. Tamaño:", len(contenido))

        patrones = [
            "ConfigMenu",
            "configBtn",
            "Remote Setting",
            "login",
            "VideoPlayTool",
            "Cmd-WebLocalCtrl",
            "SystemFunction",
            "NetWork",
            "RTSP",
            "ONVIF"
        ]

        for patron in patrones:
            coincidencias = list(
                re.finditer(patron, contenido, re.I)
            )

            if coincidencias:
                print(f"\n[{patron}] encontrado:")
                for m in coincidencias[:2]:
                    inicio = max(0, m.start() - 150)
                    fin = min(len(contenido), m.end() + 250)
                    print(contenido[inicio:fin])

    except Exception as e:
        print("No se pudo leer:", e)
'''


#####################################################
ip = "192.168.1.22"

for puerto in (554, 8899, 80, 34567):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    abierto = s.connect_ex((ip, puerto)) == 0
    print(f"Puerto {puerto}: {'ABIERTO' if abierto else 'CERRADO'}")
    s.close()