import http.client
import json
import re
import threading
import time
import urllib.parse
import cv2

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

alertas_activas = True

# Teclado táctil grande con controles individuales completos
TECLADO_TELEGRAM = {
    "keyboard": [
        [{"text": "📸 Foto 1"}, {"text": "📸 Foto 2"}, {"text": "📸 Foto 3"}, {"text": "📸 Foto 4"}],
        [{"text": "🎥 Grabar 1"}, {"text": "🎥 Grabar 2"}, {"text": "🎥 Grabar 3"}, {"text": "🎥 Grabar 4"}],
        [{"text": "👁️ Detec 1"}, {"text": "👁️ Detec 2"}, {"text": "👁️ Detec 3"}, {"text": "👁️ Detec 4"}],
        [{"text": "💡 Luz 1"}, {"text": "💡 Luz 2"}, {"text": "💡 Luz 3"}, {"text": "💡 Luz 4"}],
        [{"text": "📷 Todas Fotos"}, {"text": "🎥 Grabar Todas"}],
        [{"text": "👁️ Detec Todas"}, {"text": "🔔 Alertas ON/OFF"}],
        [{"text": "📊 Estado"}, {"text": "ℹ️ Ayuda"}],
    ],
    "resize_keyboard": False,
    "is_persistent": True,
}

# Equivalencia exacta entre cada botón y su comando
MAPEO_BOTONES = {
    "📸 foto 1": "/foto1",
    "📸 foto 2": "/foto2",
    "📸 foto 3": "/foto3",
    "📸 foto 4": "/foto4",
    "🎥 grabar 1": "/grabar1",
    "🎥 grabar 2": "/grabar2",
    "🎥 grabar 3": "/grabar3",
    "🎥 grabar 4": "/grabar4",
    "👁️ detec 1": "/deteccion1",
    "👁️ detec 2": "/deteccion2",
    "👁️ detec 3": "/deteccion3",
    "👁️ detec 4": "/deteccion4",
    "💡 luz 1": "/luz1",
    "💡 luz 2": "/luz2",
    "💡 luz 3": "/luz3",
    "💡 luz 4": "/luz4",
    "📷 todas fotos": "/foto",
    "🎥 grabar todas": "/grabar",
    "👁️ detec todas": "/deteccion",
    "🔔 alertas on/off": "/alertas",
    "📊 estado": "/estado",
    "ℹ️ ayuda": "/ayuda",
}


def alternar_alertas():
    """Activa o desactiva el envío de notificaciones a Telegram."""
    global alertas_activas
    alertas_activas = not alertas_activas
    estado = "ACTIVADAS" if alertas_activas else "DESACTIVADAS"
    print(f"[ALERTA] Notificaciones Telegram {estado}")


def enviar_mensaje_telegram(texto, incluir_teclado=True):
    """Envía un mensaje de texto con la botonera táctil adjunta."""
    token = str(TELEGRAM_TOKEN).strip()
    chat_id = str(TELEGRAM_CHAT_ID).strip()
    if not token or not chat_id:
        return

    try:
        datos = {"chat_id": chat_id, "text": texto}
        if incluir_teclado:
            datos["reply_markup"] = json.dumps(TECLADO_TELEGRAM)

        params = urllib.parse.urlencode(datos)
        conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
        conn.request("GET", f"/bot{token}/sendMessage?{params}")
        resp = conn.getresponse()
        resp.read()
        conn.close()
    except Exception as exc:
        print(f"[ALERTA] Error enviando texto a Telegram: {exc}")


def _enviar_foto_telegram(imagen_bgr, texto):
    """Envía una fotografía por HTTPS usando http.client."""
    token = str(TELEGRAM_TOKEN).strip()
    chat_id = str(TELEGRAM_CHAT_ID).strip()
    if not token or not chat_id:
        return

    try:
        exito, buffer = cv2.imencode(".jpg", imagen_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not exito:
            return
        datos_jpeg = buffer.tobytes()

        boundary = "----BoundaryAlertaCamara7MA4YWxkTrZu0gW"
        cuerpo = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
            f"{chat_id}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="caption"\r\n\r\n'
            f"{texto}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="photo"; filename="alerta.jpg"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8") + datos_jpeg + f"\r\n--{boundary}--\r\n".encode("utf-8")

        ruta = f"/bot{token}/sendPhoto"
        cabeceras = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(cuerpo)),
        }

        conn = http.client.HTTPSConnection("api.telegram.org", timeout=10)
        conn.request("POST", ruta, body=cuerpo, headers=cabeceras)
        resp = conn.getresponse()
        resp.read()
        conn.close()
    except Exception as exc:
        print(f"[ALERTA] Error enviando foto a Telegram: {exc}")


def enviar_alerta_movimiento(imagen_bgr, nombre_camara):
    """Lanza la alerta en segundo plano solo si las alertas están activadas."""
    if not alertas_activas:
        return
    copia = imagen_bgr.copy()
    mensaje = f"🚨 Movimiento detectado en: {nombre_camara}"
    threading.Thread(target=_enviar_foto_telegram, args=(copia, mensaje), daemon=True).start()


def _procesar_comando(texto, camaras):
    """Procesa botones táctiles y comandos individuales o globales."""
    entrada = texto.strip().lower()
    cmd = MAPEO_BOTONES.get(entrada, entrada)

    if cmd in ("/start", "/ayuda", "/help"):
        lista_cams = "\n".join(f"  {i + 1}. {c.nombre}" for i, c in enumerate(camaras))
        ayuda = (
            "🛡️ PANEL REMOTO DE CÁMARAS\n\n"
            f"Cámaras conectadas:\n{lista_cams}\n\n"
            "Usa los botones inferiores o escribe:\n"
            "• /foto1..4 — Foto individual\n"
            "• /grabar1..4 — Grabar individual\n"
            "• /deteccion1..4 — Movimiento individual\n"
            "• /luz1..4 — Luz (Auto / Blanca / IR)"
        )
        enviar_mensaje_telegram(ayuda)
        return

    if cmd == "/estado":
        lineas = [f"📊 ESTADO DEL SISTEMA\n• Alertas móvil: {'🟢 ON' if alertas_activas else '⚪ OFF'}"]
        for i, c in enumerate(camaras):
            grab = "🔴 REC" if getattr(c, "grabando", False) else "⚪ OFF"
            det = "🟢 ON" if getattr(c, "deteccion_activa", False) else "⚪ OFF"
            luz = getattr(c, "modo_luz_actual", "AUTO")
            lineas.append(f"{i + 1}. {c.nombre}: Grab {grab} | Det {det} | Luz {luz}")
        enviar_mensaje_telegram("\n".join(lineas))
        return

    if cmd == "/alertas":
        alternar_alertas()
        enviar_mensaje_telegram(f"🔔 Alertas al móvil: {'ACTIVADAS 🟢' if alertas_activas else 'SILENCIADAS ⚪'}.")
        return

    # Extrae la acción y el número opcional de cámara (/foto1, /grabar2, /deteccion3, /luz4)
    coincidencia = re.match(r"^/(foto|grabar|deteccion|luz)(\d+)?$", cmd)
    if not coincidencia:
        enviar_mensaje_telegram("❓ Comando no reconocido. Pulsa /start para actualizar los botones.")
        return

    accion, num_str = coincidencia.groups()

    if num_str is not None:
        idx = int(num_str) - 1
        if idx < 0 or idx >= len(camaras):
            enviar_mensaje_telegram(f"⚠️ La cámara {num_str} no existe (hay {len(camaras)} cámaras).")
            return
        objetivos = [camaras[idx]]
    else:
        objetivos = camaras

    if accion == "foto":
        for c in objetivos:
            with c.lock:
                frame = c.frame.copy() if getattr(c, "frame", None) is not None else None
            if frame is not None:
                _enviar_foto_telegram(frame, f"📷 {c.nombre}")
            else:
                enviar_mensaje_telegram(f"⚠️ {c.nombre} aún no tiene imagen disponible.")

    elif accion == "grabar":
        respuestas = []
        for c in objetivos:
            if hasattr(c, "alternar_grabacion"):
                c.alternar_grabacion()
                estado = "INICIADA 🔴" if getattr(c, "grabando", False) else "DETENIDA ⏹️"
                respuestas.append(f"🎥 {c.nombre}: Grabación {estado}")
        enviar_mensaje_telegram("\n".join(respuestas))

    elif accion == "deteccion":
        respuestas = []
        for c in objetivos:
            if hasattr(c, "alternar_deteccion"):
                c.alternar_deteccion()
                estado = "ACTIVADA 🟢" if getattr(c, "deteccion_activa", False) else "DESACTIVADA ⚪"
                respuestas.append(f"👁️ {c.nombre}: Detección {estado}")
        enviar_mensaje_telegram("\n".join(respuestas))

    elif accion == "luz":
        ciclo = {"AUTO": "BLANCA", "BLANCA": "IR", "IR": "AUTO"}
        nombres_bonitos = {
            "BLANCA": "Luz BLANCA ☀️",
            "IR": "Infrarrojos (IR) 🌙",
            "AUTO": "Luz AUTOMÁTICA 🔄",
        }
        respuestas = []
        for c in objetivos:
            if hasattr(c, "cambiar_luz_led"):
                actual = str(getattr(c, "modo_luz_actual", "AUTO")).upper()
                if actual not in ciclo:
                    actual = "AUTO"
                siguiente = ciclo[actual]
                c.cambiar_luz_led(siguiente)
                respuestas.append(f"💡 {c.nombre}: {nombres_bonitos[siguiente]}")
            else:
                respuestas.append(f"⚠️ {c.nombre}: No soporta control de luz.")
        enviar_mensaje_telegram("\n".join(respuestas))


def iniciar_bot_comandos(camaras):
    """Hilo en segundo plano que escucha botones y comandos de Telegram."""
    token = str(TELEGRAM_TOKEN).strip()
    chat_autorizado = str(TELEGRAM_CHAT_ID).strip()

    if not token or not chat_autorizado:
        return

    def bucle_escucha():
        ultimo_update_id = 0
        print("[TELEGRAM] Bot con teclado táctil escuchando órdenes...")

        while True:
            try:
                ruta = f"/bot{token}/getUpdates?offset={ultimo_update_id + 1}&timeout=20"
                conn = http.client.HTTPSConnection("api.telegram.org", timeout=25)
                conn.request("GET", ruta)
                resp = conn.getresponse()
                datos = json.loads(resp.read().decode("utf-8", errors="ignore"))
                conn.close()

                if datos.get("ok"):
                    for update in datos.get("result", []):
                        ultimo_update_id = update["update_id"]
                        msg = update.get("message", {})
                        remitente_id = str(msg.get("chat", {}).get("id", ""))
                        texto = msg.get("text", "")

                        if remitente_id == chat_autorizado and texto:
                            _procesar_comando(texto, camaras)

            except Exception:
                time.sleep(3)

    threading.Thread(target=bucle_escucha, daemon=True).start()
