"""Ventana independiente para editar la configuración del sistema."""
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    RUTA_BASE,
    CONFIG_CAMARAS_RTSP, CONFIG_PATIO, MINUTOS_POR_BLOQUE_VIDEO,
    SENSIBILIDAD_MOVIMIENTO, COOLDOWN_CAPTURA_SEG,
    INTERVALO_FOTOGRAMA_AUTO_SEG, DISPOSITIVO_SALIDA_AUDIO,
    TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
)

ARCHIVO_CONFIG = os.path.join(RUTA_BASE, "config.json")



def leer_guardados():
    try:
        with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def iniciar():
    guardados = leer_guardados()
    camaras_guardadas = guardados.get("camaras_rtsp", CONFIG_CAMARAS_RTSP)
    patio_guardado = guardados.get("patio", CONFIG_PATIO)

    root = tk.Tk()
    root.title("Configuración - Videovigilancia")
    root.geometry("720x650")
    root.minsize(650, 560)
    root.configure(bg="#202832")

    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass
    estilo.configure("TFrame", background="#202832")
    estilo.configure("TLabel", background="#202832", foreground="#f1f4f8")
    estilo.configure("TButton", padding=7)
    estilo.configure("TNotebook", background="#202832")
    estilo.configure("TNotebook.Tab", padding=(12, 7))

    encabezado = ttk.Label(root, text="CONFIGURACIÓN DEL SISTEMA",
                           font=("Segoe UI", 16, "bold"))
    encabezado.pack(anchor="w", padx=18, pady=(16, 4))
    ttk.Label(root, text="Los cambios de conexión se aplicarán al reiniciar el programa.",
              foreground="#b9c5d3").pack(anchor="w", padx=18, pady=(0, 12))

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=16, pady=6)

    tab_camaras = ttk.Frame(notebook, padding=12)
    tab_grabacion = ttk.Frame(notebook, padding=16)
    tab_general = ttk.Frame(notebook, padding=16)
    notebook.add(tab_camaras, text="Cámaras")
    notebook.add(tab_grabacion, text="Grabación y detección")
    notebook.add(tab_general, text="General")

    campos_camaras = []

    def campo(parent, etiqueta, valor, ocultar=False, ancho=34):
        fila = ttk.Frame(parent)
        fila.pack(fill="x", pady=3)
        ttk.Label(fila, text=etiqueta, width=18).pack(side="left")
        entrada = ttk.Entry(fila, width=ancho, show="*" if ocultar else "")
        entrada.pack(side="left", fill="x", expand=True)
        entrada.insert(0, str(valor))
        return entrada

    # Desplazamiento vertical para que quepan todas las cámaras.
    lienzo = tk.Canvas(tab_camaras, bg="#202832", highlightthickness=0)
    barra = ttk.Scrollbar(tab_camaras, orient="vertical", command=lienzo.yview)
    contenido = ttk.Frame(lienzo, padding=(4, 4, 12, 4))
    contenido.bind("<Configure>", lambda _e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.create_window((0, 0), window=contenido, anchor="nw")
    lienzo.configure(yscrollcommand=barra.set)
    lienzo.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    for i, cfg in enumerate(camaras_guardadas):
        grupo = ttk.LabelFrame(contenido, text=f"Cámara RTSP {i + 1}", padding=9)
        grupo.pack(fill="x", pady=6)
        entradas = {}
        for clave, etiqueta, secreto in (
            ("nombre", "Nombre", False), ("ip", "Dirección IP", False),
            ("usuario", "Usuario", False), ("password", "Contraseña", True),
            ("puerto_rtsp", "Puerto RTSP", False), ("puerto_onvif", "Puerto ONVIF", False),
            ("puerto_netip", "Puerto NetIP", False), ("canal", "Canal", False),
            ("stream", "Stream", False),
        ):
            entradas[clave] = campo(grupo, etiqueta, cfg.get(clave, ""), secreto)
        campos_camaras.append(entradas)

    grupo_patio = ttk.LabelFrame(contenido, text="Cámara DVRIP - Patio", padding=9)
    grupo_patio.pack(fill="x", pady=6)
    entradas_patio = {}
    for clave, etiqueta, secreto in (
        ("nombre", "Nombre", False), ("ip", "Dirección IP", False),
        ("usuario", "Usuario", False), ("password", "Contraseña", True),
        ("puerto_netip", "Puerto NetIP", False),
    ):
        entradas_patio[clave] = campo(grupo_patio, etiqueta, patio_guardado.get(clave, ""), secreto)

    canales = campo(grupo_patio, "Canales (separados por coma)",
                    ",".join(map(str, patio_guardado.get("canales", (0, 1)))))

    # Parámetros de grabación y detección.
    valores_grab = guardados.get("parametros", {})
    entradas_grab = {}
    for clave, etiqueta, defecto in (
        ("minutos_por_bloque_video", "Minutos por vídeo", valores_grab.get("minutos_por_bloque_video", MINUTOS_POR_BLOQUE_VIDEO)),
        ("sensibilidad_movimiento", "Sensibilidad movimiento", valores_grab.get("sensibilidad_movimiento", SENSIBILIDAD_MOVIMIENTO)),
        ("cooldown_captura_seg", "Espera entre capturas (s)", valores_grab.get("cooldown_captura_seg", COOLDOWN_CAPTURA_SEG)),
        ("intervalo_fotograma_auto_seg", "Intervalo captura auto (s)", valores_grab.get("intervalo_fotograma_auto_seg", INTERVALO_FOTOGRAMA_AUTO_SEG)),
    ):
        entradas_grab[clave] = campo(tab_grabacion, etiqueta, defecto)

    carpetas_actuales = guardados.get("carpetas", {})
    entradas_carpetas = {}
    for clave, etiqueta, defecto in (
        ("grabaciones", "Carpeta de vídeos", "grabaciones"),
        ("capturas_movimiento", "Capturas movimiento", "capturas_movimiento"),
        ("capturas_fotogramas", "Fotogramas", "capturas_fotogramas"),
    ):
        entradas_carpetas[clave] = campo(tab_grabacion, etiqueta, carpetas_actuales.get(clave, defecto), ancho=38)

    audio_guardado = guardados.get("dispositivo_salida_audio", DISPOSITIVO_SALIDA_AUDIO)
    entrada_audio = campo(tab_general, "Dispositivo salida audio", audio_guardado)
    token_guardado = guardados.get("telegram_token", TELEGRAM_TOKEN)
    chat_guardado = guardados.get("telegram_chat_id", TELEGRAM_CHAT_ID)
    entrada_token = campo(tab_general, "Token Bot Telegram", token_guardado, ocultar=True, ancho=38)
    entrada_chat = campo(tab_general, "Chat ID Telegram", chat_guardado, ancho=38)

    ttk.Label(tab_general, text="Los cambios se guardan en config.json y se cargan al iniciar la aplicación.",
              foreground="#b9c5d3", wraplength=560).pack(anchor="w", pady=(14, 4))

    def entero(entrada, nombre):
        try:
            return int(entrada.get().strip())
        except ValueError:
            raise ValueError(f"El campo '{nombre}' debe ser un número entero.")

    def guardar():
        try:
            lista_camaras = []
            for i, entradas in enumerate(campos_camaras):
                original = dict(camaras_guardadas[i])
                for clave, entrada in entradas.items():
                    original[clave] = entrada.get().strip()
                for clave in ("puerto_rtsp", "puerto_onvif", "puerto_netip", "canal", "stream"):
                    original[clave] = entero(entradas[clave], clave)
                lista_camaras.append(original)

            patio = dict(patio_guardado)
            for clave, entrada in entradas_patio.items():
                patio[clave] = entrada.get().strip()
            patio["puerto_netip"] = entero(entradas_patio["puerto_netip"], "Puerto NetIP patio")
            try:
                patio["canales"] = tuple(int(x.strip()) for x in canales.get().split(",") if x.strip())
            except ValueError:
                raise ValueError("Los canales del Patio deben ser números separados por comas.")
            if not patio["canales"]:
                raise ValueError("Debe indicarse al menos un canal para el Patio.")

            parametros = {k: entero(v, k) for k, v in entradas_grab.items()}
            dispositivo = entero(entrada_audio, "Dispositivo salida audio")
            datos = {
                "camaras_rtsp": lista_camaras,
                "patio": patio,
                "parametros": parametros,
                "carpetas": {k: v.get().strip() for k, v in entradas_carpetas.items()},
                "dispositivo_salida_audio": dispositivo,
                "telegram_token": entrada_token.get().strip(),
                "telegram_chat_id": entrada_chat.get().strip(),
            }
            with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            messagebox.showinfo("Configuración guardada",
                                "Los cambios se han guardado. Reinicia la videovigilancia para aplicarlos.",
                                parent=root)
        except (ValueError, OSError) as exc:
            messagebox.showerror("No se pudo guardar", str(exc), parent=root)

    def restaurar():
        if not messagebox.askyesno("Restaurar", "¿Quieres descartar los cambios guardados y volver a los valores de config.py?", parent=root):
            return
        try:
            if os.path.exists(ARCHIVO_CONFIG):
                os.remove(ARCHIVO_CONFIG)
            messagebox.showinfo("Restaurado", "Se han eliminado los ajustes personalizados. Reinicia la aplicación.", parent=root)
            root.destroy()
        except OSError as exc:
            messagebox.showerror("Error", str(exc), parent=root)

    pie = ttk.Frame(root, padding=(16, 10))
    pie.pack(fill="x")
    ttk.Button(pie, text="Restaurar valores", command=restaurar).pack(side="left")
    ttk.Button(pie, text="Cancelar", command=root.destroy).pack(side="right", padx=(8, 0))
    ttk.Button(pie, text="Guardar", command=guardar).pack(side="right")
    root.mainloop()


if __name__ == "__main__":
    iniciar()
