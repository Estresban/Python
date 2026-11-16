# ==============================================================================
# GUÍA DE CONTROLES - CENTRAL DE SEGURIDAD 4 CÁMARAS iCSee (XM80 + DVRIP)
# ==============================================================================
# [1, 2, 3, 4] -> Selecciona la cámara activa (o haz clic sobre su imagen).
# [RATÓN]      -> Clic en los botones "ESCUCHAR" o "HABLAR" de cada cámara.
# [V]          -> Activar/Silenciar AUDIO de la cámara seleccionada.
# [T]          -> Activar/Desactivar MICRÓFONO PC hacia la cámara seleccionada.
# [W, D, S, A] -> Girar cámara seleccionada (Arriba/Dcha/Abajo/Izda).
# [+] / [-]    -> Zoom óptico en cámara DVRIP (acercar / alejar).
# [Z] / [X]    -> Zoom digital en lente inferior (acercar / alejar).
# [L]          -> Encender LEDs de LUZ BLANCA (visión nocturna a color).
# [I]          -> Encender LEDs INFRARROJOS (visión nocturna en blanco y negro).
# [O]          -> Poner iluminación en modo AUTOMÁTICO inteligente.
# [M]          -> ACTIVAR / DESACTIVAR detección de movimiento en las 4 cámaras.
# [R]          -> ACTIVAR / DESACTIVAR grabación de video (.mp4) en las 4.
# [F]          -> ACTIVAR / DESACTIVAR captura periódica de fotogramas en las 4.
# [C]          -> Tomar una CAPTURA DE FOTO manual de la cámara seleccionada.
# [Q]          -> Cerrar conexiones de forma segura y salir del programa.
# ==============================================================================

from datetime import datetime
import hashlib
import json
import os
import queue
import socket
import struct
import subprocess
import threading
import time
import cv2
from dvrip import DVRIPCam
import numpy as np
from onvif import ONVIFCamera
import sounddevice as sd

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# --- CONFIGURACIÓN ---
CONFIG_CAMARAS_RTSP = [
    {
        "nombre": "",
        "ip": "",
        "usuario": "",
        "password": "",
        "puerto_rtsp": 554,
        "puerto_onvif": 8899,
        "puerto_netip": 34567,
        "canal": 1,
        "stream": 0,
    },
    {
        "nombre": "",
        "ip": "",
        "usuario": "",
        "password": "",
        "puerto_rtsp": 554,
        "puerto_onvif": 8899,
        "puerto_netip": 34567,
        "canal": 1,
        "stream": 0,
    },
    {
        "nombre": "",
        "ip": "",
        "usuario": "",
        "password": "",
        "puerto_rtsp": 554,
        "puerto_onvif": 8899,
        "puerto_netip": 34567,
        "canal": 1,
        "stream": 0,
    },
]

# La cuarta cámara (Patio) usa DVRIP: dos canales/lentes independientes (0 y 1).
CONFIG_PATIO = {
    "nombre": "",
    "ip": "",
    "usuario": "",
    "password": "",
    "puerto_netip": 34567,
    "canales": (0, 1),  # 0 = lente inferior; 1 = lente superior
}

# Tamaño de cada recuadro en la cuadrícula 2x2 (Total ventana: 1280x720)
ANCHO_CELDA = 640
ALTO_CELDA = 360
ALTO_LENTE_DVRIP = ALTO_CELDA // 2  # 180 px por lente apilada

MINUTOS_POR_BLOQUE_VIDEO = 10
SENSIBILIDAD_MOVIMIENTO = 1200
COOLDOWN_CAPTURA_SEG = 5
INTERVALO_FOTOGRAMA_AUTO_SEG = 10

os.makedirs("grabaciones", exist_ok=True)
os.makedirs("capturas_movimiento", exist_ok=True)
os.makedirs("capturas_fotogramas", exist_ok=True)


# ==============================================================================
# UTILIDADES DE PROTOCOLO Y AUDIO (G.711 A-LAW <-> PCM16)
# ==============================================================================

def hash_xmeye(password):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    res = ""
    md5_bytes = hashlib.md5(password.encode()).digest()
    for i in range(0, 16, 2):
        val = (md5_bytes[i] + md5_bytes[i + 1]) % 62
        res += chars[val]
    return res


def alaw_a_pcm(datos):
    datos = np.frombuffer(datos, dtype=np.uint8) ^ 0x55
    valor = ((datos & 0x0F).astype(np.int16) << 4) + 8
    segmento = (datos & 0x70) >> 4
    valor += np.where(segmento >= 1, 0x100, 0)
    valor = np.where(segmento > 1, valor << (segmento - 1), valor)
    return np.where((datos & 0x80) != 0, valor, -valor).astype(np.int16)


def pcm16_a_alaw(samples_int16):
    pcm = np.clip(samples_int16.astype(np.int32), -32768, 32767)
    sign = np.where(pcm >= 0, 0x80, 0x00)
    pcm = np.where(pcm < 0, -pcm - 1, pcm)

    exp = np.zeros_like(pcm)
    for bit in range(1, 8):
        cond = pcm >= (256 << (bit - 1))
        exp = np.where(cond, bit, exp)

    mantissa = np.where(
        exp == 0,
        (pcm >> 4) & 0x0F,
        (pcm >> (exp + 3)) & 0x0F,
    )
    alaw = (sign | (exp << 4) | mantissa) ^ 0x55
    return alaw.astype(np.uint8).tobytes()


# ==============================================================================
# CÁMARAS RTSP + ONVIF + NETIP (CÁMARAS 1, 2 Y 3)
# ==============================================================================

class CamaraAvanzada:
    def __init__(self, cfg, indice):
        self.cfg = cfg
        self.indice = indice
        self.nombre = cfg["nombre"]
        self.url = (
            f"rtsp://{cfg['ip']}:{cfg['puerto_rtsp']}/user={cfg['usuario']}_"
            f"password={cfg['password']}_channel={cfg['canal']}_"
            f"stream={cfg['stream']}.sdp"
        )

        self.frame = None
        self.conectada = False
        self.detener = False

        # Interruptores de estado (movimiento desactivado por defecto)
        self.grabando = False
        self.deteccion_activa = False
        self.captura_auto_activa = False
        self.escuchando_audio = False
        self.hablando_micro = False

        self.movimiento_detectado = False
        self.modo_luz_actual = "Auto"

        # Coordenadas locales de botones dentro de la celda (640x360)
        self.btn_escuchar = (15, 315, 145, 348)
        self.btn_hablar = (155, 315, 285, 348)

        # Procesos de audio
        self.proceso_ffplay = None
        self.hilo_micro = None

        # Grabación, movimiento y fotogramas
        self.video_writer = None
        self.inicio_bloque = 0
        self.fondo_gris = None
        self.ultima_captura_mov = 0
        self.ultimo_fotograma_auto = 0

        # Zoom digital en lente inferior
        self.zoom_digital = 1.0

        # Control PTZ ONVIF
        self.ptz = None
        self.media_profile = None
        threading.Thread(target=self._conectar_onvif, daemon=True).start()

        # Hilo de video
        self.hilo = threading.Thread(target=self._bucle_video, daemon=True)
        self.hilo.start()

    def _conectar_onvif(self):
        try:
            cam = ONVIFCamera(
                self.cfg["ip"],
                self.cfg["puerto_onvif"],
                self.cfg["usuario"],
                self.cfg["password"],
            )
            media = cam.create_media_service()
            self.ptz = cam.create_ptz_service()
            perfiles = media.GetProfiles()
            if perfiles:
                self.media_profile = perfiles[0]
            print(f"[{self.nombre}] ONVIF (PTZ) conectado correctamente.")
        except Exception as e:
            print(f"[{self.nombre}] ONVIF no disponible ({e}).")

    def mover_ptz(self, pan=0.0, tilt=0.0, zoom=0.0):
        if not self.ptz or not self.media_profile:
            print(f"[{self.nombre}] PTZ no conectado.")
            return

        def _enviar_orden():
            try:
                req = self.ptz.create_type("ContinuousMove")
                req.ProfileToken = self.media_profile.token

                if zoom != 0.0:
                    req.Velocity = {"Zoom": {"x": zoom}}
                else:
                    req.Velocity = {"PanTilt": {"x": pan, "y": tilt}}

                self.ptz.ContinuousMove(req)
                time.sleep(0.4)
                self.ptz.Stop({"ProfileToken": self.media_profile.token})
            except Exception as e:
                print(f"[{self.nombre}] Error PTZ/Zoom: {e}")

        threading.Thread(target=_enviar_orden, daemon=True).start()

    def cambiar_zoom(self, incremento):
        self.zoom_digital = max(1.0, min(4.0, self.zoom_digital + incremento))
        print(f"[{self.nombre}] Zoom: {self.zoom_digital:.1f}x")

    def cambiar_luz_led(self, modo):
        self.modo_luz_actual = modo

        def _enviar_comando_netip():
            mapa_workmode = {"BLANCA": "KeepOpen", "IR": "Close", "AUTO": "Auto"}
            work_mode = mapa_workmode.get(modo, "Auto")

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.cfg["ip"], self.cfg["puerto_netip"]))

                login_payload = json.dumps({
                    "EncryptType": "MD5",
                    "LoginType": "DVRIP-Web",
                    "PassWord": hash_xmeye(self.cfg["password"]),
                    "UserName": self.cfg["usuario"],
                }).encode()

                cabecera_login = (
                    struct.pack("<BB2xII2xHI", 0xFF, 0x00, 0, 0, 1000, len(login_payload) + 2)
                    + login_payload
                    + b"\x0a\x00"
                )
                sock.sendall(cabecera_login)
                resp_login = sock.recv(1024)
                session_id = struct.unpack("<I", resp_login[4:8])[0] if len(resp_login) >= 8 else 0

                luz_payload = json.dumps({
                    "Name": "Camera.WhiteLight",
                    "SessionID": f"0x{session_id:08X}",
                    "Camera.WhiteLight": {
                        "WorkMode": work_mode,
                        "WorkPeriod": {
                            "EHour": 23,
                            "EMinute": 59,
                            "Enable": 1,
                            "SHour": 0,
                            "SMinute": 0,
                        },
                    },
                }).encode()

                cabecera_luz = (
                    struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, 1, 1040, len(luz_payload) + 2)
                    + luz_payload
                    + b"\x0a\x00"
                )
                sock.sendall(cabecera_luz)
                resp_luz = sock.recv(1024)
                sock.close()

                texto_resp = resp_luz[20:].decode(errors="ignore").strip()
                print(f"[{self.nombre}] Orden LED ({modo}) -> Respuesta: {texto_resp}")

            except Exception as e:
                print(f"[{self.nombre}] Error conectando al puerto 34567: {e}")

        threading.Thread(target=_enviar_comando_netip, daemon=True).start()

    def detener_audio(self):
        if self.escuchando_audio:
            self.escuchando_audio = False
            if self.proceso_ffplay:
                self.proceso_ffplay.terminate()
                self.proceso_ffplay = None
        if self.hablando_micro:
            self.hablando_micro = False

    def alternar_escuchar_audio(self):
        self.escuchando_audio = not self.escuchando_audio
        if self.escuchando_audio:
            try:
                cmd = [
                    "ffplay", "-nodisp", "-vn",
                    "-rtsp_transport", "tcp",
                    "-fflags", "nobuffer",
                    "-flags", "low_delay",
                    self.url,
                ]
                self.proceso_ffplay = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                print(f"[{self.nombre}] Audio de la cámara: ACTIVADO (Escuchando)")
            except FileNotFoundError:
                self.escuchando_audio = False
                print(f"[{self.nombre}] ERROR: No se encontró 'ffplay'. Instala FFmpeg.")
        else:
            if self.proceso_ffplay:
                self.proceso_ffplay.terminate()
                self.proceso_ffplay = None
            print(f"[{self.nombre}] Audio de la cámara: SILENCIADO")

    def alternar_hablar_micro(self):
        self.hablando_micro = not self.hablando_micro
        if self.hablando_micro:
            print(f"[{self.nombre}] Micrófono PC -> Altavoz cámara: ACTIVADO")
            self.hilo_micro = threading.Thread(target=self._bucle_enviar_voz, daemon=True)
            self.hilo_micro.start()
        else:
            print(f"[{self.nombre}] Micrófono PC -> Altavoz cámara: APAGADO")

    def _bucle_enviar_voz(self):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((self.cfg["ip"], self.cfg["puerto_netip"]))

            login_payload = json.dumps({
                "EncryptType": "MD5",
                "LoginType": "DVRIP-Web",
                "PassWord": hash_xmeye(self.cfg["password"]),
                "UserName": self.cfg["usuario"],
            }).encode()

            cab_login = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, 0, 0, 1000, len(login_payload) + 2)
                + login_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_login)
            resp = sock.recv(1024)
            session_id = struct.unpack("<I", resp[4:8])[0] if len(resp) >= 8 else 0

            talk_payload = json.dumps({
                "Name": "OPTalk",
                "SessionID": f"0x{session_id:08X}",
                "OPTalk": {
                    "Action": "Start",
                    "AudioFormat": {
                        "BitRate": 128,
                        "EncodeType": "G711_ALAW",
                        "SampleBit": 8,
                        "SampleRate": 8000,
                    },
                },
            }).encode()

            cab_talk = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, 1, 1430, len(talk_payload) + 2)
                + talk_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_talk)
            sock.recv(1024)

            chunk_size = 320
            seq = 2
            with sd.InputStream(
                samplerate=8000, channels=1, dtype="int16", blocksize=chunk_size
            ) as stream_mic:
                while self.hablando_micro and not self.detener:
                    pcm_array, _ = stream_mic.read(chunk_size)
                    alaw_data = pcm16_a_alaw(pcm_array.flatten())

                    audio_pkt = (
                        b"\x00\x00\x01\xfa\x0e\x02"
                        + struct.pack("<H", len(alaw_data))
                        + alaw_data
                    )
                    cab_audio = (
                        struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1432, len(audio_pkt))
                        + audio_pkt
                    )
                    sock.sendall(cab_audio)
                    seq += 1

            stop_payload = json.dumps({
                "Name": "OPTalk",
                "SessionID": f"0x{session_id:08X}",
                "OPTalk": {"Action": "Stop"},
            }).encode()
            cab_stop = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1430, len(stop_payload) + 2)
                + stop_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_stop)

        except Exception as e:
            print(f"[{self.nombre}] Error en micrófono bidireccional: {e}")
            self.hablando_micro = False
        finally:
            if sock:
                sock.close()

    def alternar_deteccion(self):
        self.deteccion_activa = not self.deteccion_activa
        if not self.deteccion_activa:
            self.movimiento_detectado = False
            self.fondo_gris = None
        estado = "ACTIVADA" if self.deteccion_activa else "DESACTIVADA"
        print(f"[{self.nombre}] Detección de movimiento: {estado}")

    def alternar_grabacion(self):
        self.grabando = not self.grabando
        if not self.grabando and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            print(f"[{self.nombre}] Grabación de video: DETENIDA y guardada.")
        elif self.grabando:
            print(f"[{self.nombre}] Grabación de video: INICIADA.")

    def alternar_captura_auto(self):
        self.captura_auto_activa = not self.captura_auto_activa
        estado = "ACTIVADA" if self.captura_auto_activa else "DESACTIVADA"
        print(f"[{self.nombre}] Captura periódica de fotogramas ({INTERVALO_FOTOGRAMA_AUTO_SEG}s): {estado}")

    def capturar_fotograma_manual(self):
        if self.frame is not None:
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            ruta = f"capturas_fotogramas/MANUAL_{self.nombre.replace(' ', '_')}_{fecha_str}.jpg"
            cv2.imwrite(ruta, self.frame)
            print(f"[{self.nombre}] Fotograma manual guardado -> {ruta}")

    def _gestionar_grabacion(self, frame):
        if not self.grabando:
            return
        ahora = time.time()
        if self.video_writer is None or (ahora - self.inicio_bloque) >= (MINUTOS_POR_BLOQUE_VIDEO * 60):
            if self.video_writer:
                self.video_writer.release()
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta = f"grabaciones/{self.nombre.replace(' ', '_')}_{fecha_str}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(ruta, fourcc, 20.0, (ANCHO_CELDA, ALTO_CELDA))
            self.inicio_bloque = ahora
        self.video_writer.write(frame)

    def _gestionar_captura_auto(self, frame):
        if not self.captura_auto_activa:
            return
        ahora = time.time()
        if (ahora - self.ultimo_fotograma_auto) >= INTERVALO_FOTOGRAMA_AUTO_SEG:
            self.ultimo_fotograma_auto = ahora
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta = f"capturas_fotogramas/AUTO_{self.nombre.replace(' ', '_')}_{fecha_str}.jpg"
            cv2.imwrite(ruta, frame)
            print(f"[{self.nombre}] Fotograma periódico guardado -> {ruta}")

    def _detectar_movimiento(self, frame):
        if not self.deteccion_activa:
            return False

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.GaussianBlur(gris, (21, 21), 0)

        if self.fondo_gris is None:
            self.fondo_gris = gris
            return False

        diferencia = cv2.absdiff(self.fondo_gris, gris)
        _, umbral = cv2.threshold(diferencia, 25, 255, cv2.THRESH_BINARY)
        umbral = cv2.dilate(umbral, None, iterations=2)
        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hay_movimiento = any(cv2.contourArea(c) > SENSIBILIDAD_MOVIMIENTO for c in contornos)
        self.fondo_gris = cv2.addWeighted(self.fondo_gris, 0.95, gris, 0.05, 0)

        if hay_movimiento:
            ahora = time.time()
            if (ahora - self.ultima_captura_mov) >= COOLDOWN_CAPTURA_SEG:
                self.ultima_captura_mov = ahora
                fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_foto = f"capturas_movimiento/MOV_{self.nombre.replace(' ', '_')}_{fecha_str}.jpg"
                cv2.imwrite(ruta_foto, frame)
                print(f"¡ALERTA! Movimiento en {self.nombre} -> {ruta_foto}")

        return hay_movimiento

    def _aplicar_zoom_digital(self, frame):
        if self.zoom_digital <= 1.0:
            return frame
        h, w = frame.shape[:2]
        mitad_y = h // 2
        parte_superior = frame[:mitad_y, :]
        parte_inferior = frame[mitad_y:, :]

        nh, nw = int(mitad_y / self.zoom_digital), int(w / self.zoom_digital)
        y1, x1 = (mitad_y - nh) // 2, (w - nw) // 2
        recorte_inf = parte_inferior[y1:y1 + nh, x1:x1 + nw]
        parte_inferior_zoom = cv2.resize(recorte_inf, (w, h - mitad_y))
        return np.vstack((parte_superior, parte_inferior_zoom))

    def _bucle_video(self):
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        while not self.detener:
            if not cap.isOpened():
                self.conectada = False
                time.sleep(2)
                cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                continue

            ret, frame = cap.read()
            if ret:
                frame_redim = cv2.resize(frame, (ANCHO_CELDA, ALTO_CELDA))
                self.conectada = True
                self.movimiento_detectado = self._detectar_movimiento(frame_redim)
                self._gestionar_grabacion(frame_redim)
                self._gestionar_captura_auto(frame_redim)
                self.frame = self._aplicar_zoom_digital(frame_redim)
            else:
                self.conectada = False
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

        if self.video_writer:
            self.video_writer.release()
        cap.release()

    def obtener_imagen_ui(self, seleccionada=False):
        if self.conectada and self.frame is not None:
            img = self.frame.copy()
        else:
            img = np.zeros((ALTO_CELDA, ANCHO_CELDA, 3), dtype=np.uint8)
            cv2.putText(
                img, f"[{self.indice + 1}] {self.nombre}: Conectando...",
                (140, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
            )

        color_titulo = (0, 255, 255) if seleccionada else (0, 255, 0)
        marca_activa = " [ACTIVA]" if seleccionada else ""
        texto_titulo = (
            f"[{self.indice + 1}] {self.nombre}{marca_activa} |"
            f" Z:{self.zoom_digital:.1f}x | {self.modo_luz_actual}"
        )
        cv2.putText(img, texto_titulo, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, color_titulo, 2)

        estado_mov = "MOV:ON" if self.deteccion_activa else "MOV:OFF"
        color_mov = (0, 255, 0) if self.deteccion_activa else (140, 140, 140)
        cv2.putText(img, estado_mov, (415, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_mov, 2)

        estado_foto = "FOT:ON" if self.captura_auto_activa else "FOT:OFF"
        color_foto = (0, 255, 255) if self.captura_auto_activa else (140, 140, 140)
        cv2.putText(img, estado_foto, (495, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_foto, 2)

        if self.grabando:
            cv2.circle(img, (582, 19), 6, (0, 0, 255), -1)
            cv2.putText(img, "REC", (592, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 255), 2)

        x1, y1, x2, y2 = self.btn_escuchar
        color_btn_esc = (200, 130, 0) if self.escuchando_audio else (55, 55, 55)
        cv2.rectangle(img, (x1, y1), (x2, y2), color_btn_esc, -1)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
        txt_esc = "OYENDO [V]" if self.escuchando_audio else "ESCUCHAR [V]"
        cv2.putText(img, txt_esc, (x1 + 8, y1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        x1, y1, x2, y2 = self.btn_hablar
        color_btn_hab = (0, 0, 220) if self.hablando_micro else (55, 55, 55)
        cv2.rectangle(img, (x1, y1), (x2, y2), color_btn_hab, -1)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
        txt_hab = "HABLANDO [T]" if self.hablando_micro else "HABLAR [T]"
        cv2.putText(img, txt_hab, (x1 + 8, y1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        if self.movimiento_detectado:
            cv2.rectangle(img, (3, 3), (ANCHO_CELDA - 3, ALTO_CELDA - 3), (0, 0, 255), 4)
            cv2.putText(img, "MOVIMIENTO DETECTADO", (415, 342), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 255), 2)
        elif seleccionada:
            cv2.rectangle(img, (2, 2), (ANCHO_CELDA - 2, ALTO_CELDA - 2), (0, 255, 255), 3)

        return img


# ==============================================================================
# CUARTA CÁMARA: DVRIP CON DOS LENTES + PTZ + LUZ + AUDIO BIDIRECCIONAL
# ==============================================================================

class CamaraDVRIP:
    """Cámara lógica con dos lentes DVRIP apiladas y control completo."""

    def __init__(self, cfg, indice):
        self.cfg = cfg
        self.indice = indice
        self.nombre = cfg["nombre"]
        self.frame = None
        self.conectada = False
        self.detener = False

        # Estados de funciones (movimiento desactivado por defecto)
        self.grabando = False
        self.deteccion_activa = False
        self.captura_auto_activa = False
        self.escuchando_audio = False
        self.hablando_micro = False
        self.movimiento_detectado = False
        self.modo_luz_actual = "Auto"
        self.zoom_digital = 1.0

        self.btn_escuchar = (15, 315, 145, 348)
        self.btn_hablar = (155, 315, 285, 348)

        self.video_writer = None
        self.inicio_bloque = 0
        self.fondo_gris = None
        self.ultima_captura_mov = 0
        self.ultimo_fotograma_auto = 0

        self.lock = threading.Lock()
        self.lock_control = threading.Lock()
        self.ultima_lente = {0: None, 1: None}
        self.colas_video = {0: queue.Queue(maxsize=100), 1: queue.Queue(maxsize=100)}
        self.cola_audio = queue.Queue(maxsize=100)
        self.procesos = {}
        self.logs = {}
        self.camaras_dvrip = {}
        self.cam_control = None

        self._iniciar_dvrip()

    def _iniciar_dvrip(self):
        try:
            # 1. Sesión dedicada para PTZ
            self.cam_control = DVRIPCam(
                self.cfg["ip"], user=self.cfg["usuario"], password=self.cfg["password"]
            )
            if self.cam_control.login():
                print(f"[{self.nombre}] Sesión PTZ DVRIP iniciada.")
            else:
                print(f"[{self.nombre}] Aviso: No se pudo iniciar sesión PTZ DVRIP.")

            # 2. Conexiones de vídeo por cada lente
            for canal in self.cfg["canales"]:
                cam = DVRIPCam(
                    self.cfg["ip"], user=self.cfg["usuario"], password=self.cfg["password"]
                )
                if not cam.login():
                    raise RuntimeError(f"No se pudo iniciar sesión DVRIP en canal {canal}")
                self.camaras_dvrip[canal] = cam

                cmd = [
                    "ffmpeg", "-loglevel", "error",
                    "-f", "hevc", "-i", "pipe:0",
                    "-an", "-vf", f"scale={ANCHO_CELDA}:{ALTO_LENTE_DVRIP}",
                    "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1",
                ]
                log = open(f"ffmpeg_patio_lente_{canal}.log", "w")
                proc = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, bufsize=0
                )
                self.procesos[canal] = proc
                self.logs[canal] = log

                threading.Thread(target=self._alimentar_ffmpeg, args=(canal,), daemon=True).start()
                threading.Thread(target=self._leer_ffmpeg, args=(canal,), daemon=True).start()
                threading.Thread(
                    target=self._bucle_monitor_dvrip,
                    args=(canal,),
                    daemon=True,
                ).start()

            self.conectada = True
            print(f"[{self.nombre}] DVRIP conectado: lentes/canales {self.cfg['canales']}")
        except Exception as e:
            self.conectada = False
            print(f"[{self.nombre}] Error iniciando DVRIP: {e}")

    def _bucle_monitor_dvrip(self, canal):
        while not self.detener:
            cam = self.camaras_dvrip.get(canal)
            if not cam:
                break
            try:
                cam.start_monitor(self._crear_callback(canal), None, channel=canal)
            except Exception as e:
                if not self.detener:
                    print(f"[{self.nombre}] Reconectando canal {canal} DVRIP ({e})...")
                    time.sleep(2)
                    try:
                        cam.close()
                    except Exception:
                        pass
                    nueva_cam = DVRIPCam(
                        self.cfg["ip"], user=self.cfg["usuario"], password=self.cfg["password"]
                    )
                    if nueva_cam.login():
                        self.camaras_dvrip[canal] = nueva_cam

    def _crear_callback(self, canal):
        def callback(frame, meta, user):
            if self.detener or frame is None or not meta:
                return
            if meta.get("frame") in ("I", "P"):
                q = self.colas_video[canal]
                if q.full():
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        pass
                try:
                    q.put_nowait(bytes(frame))
                except queue.Full:
                    pass
            elif meta.get("type") == "g711a" and canal == 0 and self.escuchando_audio:
                pcm = alaw_a_pcm(frame)
                if self.cola_audio.full():
                    try:
                        self.cola_audio.get_nowait()
                    except queue.Empty:
                        pass
                try:
                    self.cola_audio.put_nowait(pcm)
                except queue.Full:
                    pass

        return callback

    def _alimentar_ffmpeg(self, canal):
        proc = self.procesos[canal]
        q = self.colas_video[canal]
        while not self.detener and proc.poll() is None:
            paquete = q.get()
            if paquete is None or self.detener:
                break
            try:
                proc.stdin.write(paquete)
                proc.stdin.flush()
            except (BrokenPipeError, OSError, ValueError):
                break


    def _leer_ffmpeg(self, canal):
        proc = self.procesos[canal]
        n = ANCHO_CELDA * ALTO_LENTE_DVRIP * 3
        buffer = bytearray()
        while not self.detener and proc.poll() is None:
            data = proc.stdout.read(65536)
            if not data:
                break
            buffer.extend(data)
            while len(buffer) >= n:
                raw = bytes(buffer[:n])
                del buffer[:n]
                img = np.frombuffer(raw, dtype=np.uint8).reshape((ALTO_LENTE_DVRIP, ANCHO_CELDA, 3)).copy()
                with self.lock:
                    self.ultima_lente[canal] = img
                    inf = self.ultima_lente[0]
                    sup = self.ultima_lente[1]
                    if inf is not None and sup is not None:
                        self.frame = np.vstack((sup, inf))

    # --- CONTROL PTZ E ILUMINACIÓN DVRIP ---
    def mover_ptz(self, pan=0.0, tilt=0.0, zoom=0.0):
        if tilt > 0:
            direccion = "DirectionUp"
        elif tilt < 0:
            direccion = "DirectionDown"
        elif pan > 0:
            direccion = "DirectionLeft"
        elif pan < 0:
            direccion = "DirectionRight"
        elif zoom > 0:
            direccion = "ZoomTile"
        elif zoom < 0:
            direccion = "ZoomWide"
        else:
            return

        def enviar_comando(preset_val):
            parametros = {
                "AUX": {"Number": 0, "Status": "On"},
                "Channel": 0,
                "MenuOpts": "Enter",
                "POINT": {"bottom": 0, "left": 0, "right": 0, "top": 0},
                "Pattern": "SetBegin",
                "Preset": preset_val,
                "Step": 4,
                "Tour": 0,
            }
            self.cam_control.set_command(
                "OPPTZControl", {"Command": direccion, "Parameter": parametros}
            )

        def ejecutar():
            if not self.cam_control:
                return
            with self.lock_control:
                try:
                    enviar_comando(65535)
                    time.sleep(0.35)
                    enviar_comando(-1)
                except Exception as e:
                    print(f"[{self.nombre}] Error PTZ ({direccion}): {e}")

        threading.Thread(target=ejecutar, daemon=True).start()

    def cambiar_luz_led(self, modo):
        self.modo_luz_actual = modo

        def _enviar_netip():
            mapa_workmode = {"BLANCA": "KeepOpen", "IR": "Close", "AUTO": "Auto"}
            work_mode = mapa_workmode.get(modo, "Auto")

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.cfg["ip"], self.cfg["puerto_netip"]))

                login_payload = json.dumps({
                    "EncryptType": "MD5",
                    "LoginType": "DVRIP-Web",
                    "PassWord": hash_xmeye(self.cfg["password"]),
                    "UserName": self.cfg["usuario"],
                }).encode()

                cab_login = (
                    struct.pack("<BB2xII2xHI", 0xFF, 0x00, 0, 0, 1000, len(login_payload) + 2)
                    + login_payload
                    + b"\x0a\x00"
                )
                sock.sendall(cab_login)
                resp_login = sock.recv(1024)
                session_id = struct.unpack("<I", resp_login[4:8])[0] if len(resp_login) >= 8 else 0

                luz_payload = json.dumps({
                    "Name": "Camera.WhiteLight",
                    "SessionID": f"0x{session_id:08X}",
                    "Camera.WhiteLight": {
                        "WorkMode": work_mode,
                        "WorkPeriod": {
                            "EHour": 23,
                            "EMinute": 59,
                            "Enable": 1,
                            "SHour": 0,
                            "SMinute": 0,
                        },
                    },
                }).encode()

                cab_luz = (
                    struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, 1, 1040, len(luz_payload) + 2)
                    + luz_payload
                    + b"\x0a\x00"
                )
                sock.sendall(cab_luz)
                resp_luz = sock.recv(1024)
                sock.close()

                texto_resp = resp_luz[20:].decode(errors="ignore").strip()
                print(f"[{self.nombre}] Luz LED -> {modo} ({work_mode}) | Respuesta: {texto_resp}")

            except Exception as e:
                print(f"[{self.nombre}] Error cambiando iluminación LED: {e}")

        threading.Thread(target=_enviar_netip, daemon=True).start()

    # --- AUDIO BIDIRECCIONAL (ESCUCHAR Y HABLAR) ---
    def alternar_escuchar_audio(self):
        self.escuchando_audio = not self.escuchando_audio
        if self.escuchando_audio:
            while not self.cola_audio.empty():
                try:
                    self.cola_audio.get_nowait()
                except queue.Empty:
                    break
            threading.Thread(target=self._reproducir_audio, daemon=True).start()
        print(f"[{self.nombre}] Escucha DVRIP: {'ACTIVADA' if self.escuchando_audio else 'SILENCIADA'}")

    def _reproducir_audio(self):
        try:
            with sd.OutputStream(device=3, samplerate=8000, channels=1, dtype="int16") as out:
                while self.escuchando_audio and not self.detener:
                    try:
                        pcm = self.cola_audio.get(timeout=0.2)
                        out.write(pcm)
                    except queue.Empty:
                        continue
        except Exception as e:
            print(f"[{self.nombre}] Error de salida de audio: {e}")
        finally:
            self.escuchando_audio = False

    def detener_audio(self):
        self.escuchando_audio = False
        self.hablando_micro = False

    def alternar_hablar_micro(self):
        self.hablando_micro = not self.hablando_micro
        if self.hablando_micro:
            print(f"[{self.nombre}] Micrófono PC -> Cámara: ACTIVADO")
            threading.Thread(target=self._bucle_enviar_voz, daemon=True).start()
        else:
            print(f"[{self.nombre}] Micrófono PC -> Cámara: APAGADO")

    def _bucle_enviar_voz(self):
        sock = None
        session_id = 0
        seq = 1
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((self.cfg["ip"], self.cfg["puerto_netip"]))

            # 1. Login
            login_payload = json.dumps({
                "EncryptType": "MD5",
                "LoginType": "DVRIP-Web",
                "PassWord": hash_xmeye(self.cfg["password"]),
                "UserName": self.cfg["usuario"],
            }).encode()

            cab_login = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, 0, 0, 1000, len(login_payload) + 2)
                + login_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_login)
            resp = sock.recv(1024)
            session_id = struct.unpack("<I", resp[4:8]) if len(resp) >= 8 else 0

            # 2. Claim (código 1434)
            claim_payload = json.dumps({
                "Name": "OPTalk",
                "SessionID": f"0x{session_id:08X}",
                "OPTalk": {
                    "Action": "Claim",
                    "AudioFormat": {
                        "BitRate": 128,
                        "EncodeType": "G711_ALAW",
                        "SampleBit": 8,
                        "SampleRate": 8000,
                    },
                },
            }).encode()

            cab_claim = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1434, len(claim_payload) + 2)
                + claim_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_claim)
            sock.recv(1024)
            seq += 1

            # 3. Start (código 1430)
            talk_payload = json.dumps({
                "Name": "OPTalk",
                "SessionID": f"0x{session_id:08X}",
                "OPTalk": {
                    "Action": "Start",
                    "AudioFormat": {
                        "BitRate": 128,
                        "EncodeType": "G711_ALAW",
                        "SampleBit": 8,
                        "SampleRate": 8000,
                    },
                },
            }).encode()

            cab_talk = (
                struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1430, len(talk_payload) + 2)
                + talk_payload
                + b"\x0a\x00"
            )
            sock.sendall(cab_talk)
            sock.recv(1024)
            seq += 1

            # 4. Captura de micrófono y envío de paquetes (código 1432)
            chunk_size = 320
            with sd.InputStream(
                samplerate=8000, channels=1, dtype="int16", blocksize=chunk_size
            ) as stream_mic:
                while self.hablando_micro and not self.detener:
                    pcm_array, _ = stream_mic.read(chunk_size)
                    alaw_data = pcm16_a_alaw(pcm_array.flatten())

                    audio_pkt = (
                        b"\x00\x00\x01\xfa\x0e\x02"
                        + struct.pack("<H", len(alaw_data))
                        + alaw_data
                    )
                    cab_audio = (
                        struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1432, len(audio_pkt))
                        + audio_pkt
                    )
                    sock.sendall(cab_audio)
                    seq += 1

        except Exception as e:
            print(f"[{self.nombre}] Error en micrófono bidireccional: {e}")
            self.hablando_micro = False
        finally:
            if sock and session_id:
                try:
                    stop_payload = json.dumps({
                        "Name": "OPTalk",
                        "SessionID": f"0x{session_id:08X}",
                        "OPTalk": {"Action": "Stop"},
                    }).encode()
                    cab_stop = (
                        struct.pack("<BB2xII2xHI", 0xFF, 0x00, session_id, seq, 1430, len(stop_payload) + 2)
                        + stop_payload
                        + b"\x0a\x00"
                    )
                    sock.sendall(cab_stop)
                    sock.recv(1024)
                except Exception:
                    pass
            if sock:
                sock.close()

    # --- ZOOM DIGITAL, DETECCIÓN, GRABACIÓN Y CAPTURAS ---
    def cambiar_zoom(self, incremento):
        self.zoom_digital = max(1.0, min(4.0, self.zoom_digital + incremento))
        print(f"[{self.nombre}] Zoom digital lente inferior: {self.zoom_digital:.1f}x")

    def _aplicar_zoom_digital(self, frame):
        if self.zoom_digital <= 1.0:
            return frame
        parte_superior = frame[:ALTO_LENTE_DVRIP, :]
        parte_inferior = frame[ALTO_LENTE_DVRIP:, :]

        nh = int(ALTO_LENTE_DVRIP / self.zoom_digital)
        nw = int(ANCHO_CELDA / self.zoom_digital)
        y1 = (ALTO_LENTE_DVRIP - nh) // 2
        x1 = (ANCHO_CELDA - nw) // 2

        recorte = parte_inferior[y1:y1 + nh, x1:x1 + nw]
        parte_inferior_zoom = cv2.resize(recorte, (ANCHO_CELDA, ALTO_LENTE_DVRIP))
        return np.vstack((parte_superior, parte_inferior_zoom))

    def alternar_deteccion(self):
        self.deteccion_activa = not self.deteccion_activa
        if not self.deteccion_activa:
            self.fondo_gris = None
            self.movimiento_detectado = False
        print(f"[{self.nombre}] Detección: {'ON' if self.deteccion_activa else 'OFF'}")

    def alternar_grabacion(self):
        self.grabando = not self.grabando
        if not self.grabando and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        print(f"[{self.nombre}] Grabación: {'ON' if self.grabando else 'OFF'}")

    def alternar_captura_auto(self):
        self.captura_auto_activa = not self.captura_auto_activa
        print(f"[{self.nombre}] Captura periódica: {'ON' if self.captura_auto_activa else 'OFF'}")

    def capturar_fotograma_manual(self):
        with self.lock:
            base = self.frame.copy() if self.frame is not None else None
        if base is not None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            path = f"capturas_fotogramas/MANUAL_{self.nombre}_{name}.jpg"
            cv2.imwrite(path, base)
            print(f"[{self.nombre}] Foto manual guardada -> {path}")

    def _procesar_frame(self, frame):
        now = time.time()
        if self.deteccion_activa:
            gris = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            if self.fondo_gris is None:
                self.fondo_gris = gris
            else:
                diff = cv2.absdiff(self.fondo_gris, gris)
                _, th = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                th = cv2.dilate(th, None, iterations=2)
                contornos, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                self.movimiento_detectado = any(
                    cv2.contourArea(c) > SENSIBILIDAD_MOVIMIENTO for c in contornos
                )
                self.fondo_gris = cv2.addWeighted(self.fondo_gris, 0.95, gris, 0.05, 0)
                if self.movimiento_detectado and now - self.ultima_captura_mov >= COOLDOWN_CAPTURA_SEG:
                    self.ultima_captura_mov = now
                    path = f"capturas_movimiento/MOV_{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
                    cv2.imwrite(path, frame)
                    print(f"¡ALERTA! Movimiento en {self.nombre} -> {path}")

        if self.grabando:
            if self.video_writer is None or now - self.inicio_bloque >= MINUTOS_POR_BLOQUE_VIDEO * 60:
                if self.video_writer:
                    self.video_writer.release()
                path = f"grabaciones/{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.mp4"
                self.video_writer = cv2.VideoWriter(
                    path, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (ANCHO_CELDA, ALTO_CELDA)
                )
                self.inicio_bloque = now
            self.video_writer.write(frame)

        if self.captura_auto_activa and now - self.ultimo_fotograma_auto >= INTERVALO_FOTOGRAMA_AUTO_SEG:
            self.ultimo_fotograma_auto = now
            path = f"capturas_fotogramas/AUTO_{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
            cv2.imwrite(path, frame)
            print(f"[{self.nombre}] Fotograma periódico guardado -> {path}")

    def obtener_imagen_ui(self, seleccionada=False):
        with self.lock:
            base = self.frame.copy() if self.frame is not None else None

        if base is None:
            img = np.zeros((ALTO_CELDA, ANCHO_CELDA, 3), dtype=np.uint8)
            cv2.putText(
                img, f"[{self.indice + 1}] {self.nombre}: esperando DVRIP...",
                (80, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
            )
            return img

        self._procesar_frame(base)
        img = self._aplicar_zoom_digital(base)

        color_titulo = (0, 255, 255) if seleccionada else (0, 255, 0)
        marca_activa = " [ACTIVA]" if seleccionada else ""
        texto_titulo = (
            f"[{self.indice + 1}] {self.nombre}{marca_activa} |"
            f" Z:{self.zoom_digital:.1f}x | {self.modo_luz_actual}"
        )
        cv2.putText(img, texto_titulo, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, color_titulo, 2)

        estado_mov = "MOV:ON" if self.deteccion_activa else "MOV:OFF"
        color_mov = (0, 255, 0) if self.deteccion_activa else (140, 140, 140)
        cv2.putText(img, estado_mov, (415, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_mov, 2)

        estado_foto = "FOT:ON" if self.captura_auto_activa else "FOT:OFF"
        color_foto = (0, 255, 255) if self.captura_auto_activa else (140, 140, 140)
        cv2.putText(img, estado_foto, (495, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_foto, 2)

        if self.grabando:
            cv2.circle(img, (582, 19), 6, (0, 0, 255), -1)
            cv2.putText(img, "REC", (592, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 255), 2)

        for rect, active, txt_on, txt_off in (
            (self.btn_escuchar, self.escuchando_audio, "OYENDO [V]", "ESCUCHAR [V]"),
            (self.btn_hablar, self.hablando_micro, "HABLANDO [T]", "HABLAR [T]"),
        ):
            x1, y1, x2, y2 = rect
            color = (200, 130, 0) if (active and rect == self.btn_escuchar) else (
                (0, 0, 220) if active else (55, 55, 55)
            )
            cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
            cv2.putText(
                img, txt_on if active else txt_off, (x1 + 8, y1 + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1,
            )

        if self.movimiento_detectado:
            cv2.rectangle(img, (3, 3), (ANCHO_CELDA - 3, ALTO_CELDA - 3), (0, 0, 255), 4)
            cv2.putText(img, "MOVIMIENTO DETECTADO", (415, 342), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 255), 2)
        elif seleccionada:
            cv2.rectangle(img, (2, 2), (ANCHO_CELDA - 2, ALTO_CELDA - 2), (0, 255, 255), 3)

        return img

    def cerrar(self):
        self.detener = True
        self.detener_audio()
        for canal, cam in self.camaras_dvrip.items():
            try:
                cam.stop_monitor()
                cam.close()
            except Exception:
                pass
            try:
                self.colas_video[canal].put_nowait(None)
            except queue.Full:
                pass
        if self.cam_control:
            try:
                self.cam_control.close()
            except Exception:
                pass
        for proc in self.procesos.values():
            try:
                if proc.stdin:
                    proc.stdin.close()
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        for log in self.logs.values():
            try:
                log.close()
            except Exception:
                pass
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None


# ==============================================================================
# ARRANQUE Y VENTANA ÚNICA 2x2
# ==============================================================================

camaras = [CamaraAvanzada(cfg, i) for i, cfg in enumerate(CONFIG_CAMARAS_RTSP)]
camaras.append(CamaraDVRIP(CONFIG_PATIO, 3))
camara_activa = 0
NOMBRE_VENTANA = "Central de Seguridad - 4 Camaras"
ANCHO_TOTAL_BASE = ANCHO_CELDA * 2  # 1280
ALTO_TOTAL_BASE = ALTO_CELDA * 2    # 720

def activar_audio_exclusivo(indice, tipo):
    for i, cam in enumerate(camaras):
        if i != indice:
            cam.detener_audio()
    if tipo == "ESCUCHAR":
        camaras[indice].alternar_escuchar_audio()
    else:
        camaras[indice].alternar_hablar_micro()


def gestionar_clic_raton(event, x, y, flags, param):
    global camara_activa
    if event == cv2.EVENT_LBUTTONDOWN:
        # Obtener el tamaño real actual de la ventana en pantalla para escalar el clic
        try:
            _, _, win_w, win_h = cv2.getWindowImageRect(NOMBRE_VENTANA)
            if win_w > 0 and win_h > 0:
                x = int(x * (ANCHO_TOTAL_BASE / win_w))
                y = int(y * (ALTO_TOTAL_BASE / win_h))
        except Exception:
            pass

        col = 0 if x < ANCHO_CELDA else 1
        fila = 0 if y < ALTO_CELDA else 1
        idx = fila * 2 + col
        if idx >= len(camaras):
            return
        camara_activa = idx
        lx, ly = x % ANCHO_CELDA, y % ALTO_CELDA
        cam = camaras[idx]
        x1, y1, x2, y2 = cam.btn_escuchar
        if x1 <= lx <= x2 and y1 <= ly <= y2:
            activar_audio_exclusivo(idx, "ESCUCHAR")
            return
        x1, y1, x2, y2 = cam.btn_hablar
        if x1 <= lx <= x2 and y1 <= ly <= y2:
            activar_audio_exclusivo(idx, "HABLAR")

# Permitir redimensionar la ventana y ajustarla al tamaño de pantalla
cv2.namedWindow(NOMBRE_VENTANA, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(NOMBRE_VENTANA, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback(NOMBRE_VENTANA, gestionar_clic_raton)

print("\n=== CENTRAL DE SEGURIDAD INICIADA ===")
print("1-4: Seleccionar | V: Escuchar | T: Hablar | WASD: PTZ | +/-: Zoom óptico | Z/X: Zoom digital")
print("L: Luz blanca | I: Infrarrojos | O: Automático | M: Movimiento | R: Grabar | F: Fotos auto | C: Foto | Q: Salir\n")

try:
    while True:
        imagenes = [
            cam.obtener_imagen_ui(seleccionada=(i == camara_activa))
            for i, cam in enumerate(camaras)
        ]
        cuadricula = np.vstack((
            np.hstack((imagenes[0], imagenes[1])),
            np.hstack((imagenes[2], imagenes[3])),
        ))
        cv2.imshow(NOMBRE_VENTANA, cuadricula)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break
        elif tecla in (ord("1"), ord("2"), ord("3"), ord("4")):
            camara_activa = int(chr(tecla)) - 1
            print(f"Cámara activa: {camaras[camara_activa].nombre}")
        elif tecla == ord("m"):
            for cam in camaras:
                cam.alternar_deteccion()
        elif tecla == ord("r"):
            for cam in camaras:
                cam.alternar_grabacion()
        elif tecla == ord("f"):
            for cam in camaras:
                cam.alternar_captura_auto()
        elif tecla == ord("c"):
            camaras[camara_activa].capturar_fotograma_manual()
        elif tecla == ord("v"):
            activar_audio_exclusivo(camara_activa, "ESCUCHAR")
        elif tecla == ord("t"):
            activar_audio_exclusivo(camara_activa, "HABLAR")
        elif tecla == ord("w"):
            camaras[camara_activa].mover_ptz(tilt=0.3)
        elif tecla == ord("s"):
            camaras[camara_activa].mover_ptz(tilt=-0.3)
        elif tecla == ord("d"):
            camaras[camara_activa].mover_ptz(pan=-0.3)
        elif tecla == ord("a"):
            camaras[camara_activa].mover_ptz(pan=0.3)
        elif tecla in (ord("+"), ord("=")):
            camaras[camara_activa].mover_ptz(zoom=0.3)
        elif tecla == ord("-"):
            camaras[camara_activa].mover_ptz(zoom=-0.3)
        elif tecla == ord("z"):
            camaras[camara_activa].cambiar_zoom(0.1)
        elif tecla == ord("x"):
            camaras[camara_activa].cambiar_zoom(-0.1)
        elif tecla == ord("l"):
            camaras[camara_activa].cambiar_luz_led("BLANCA")
        elif tecla == ord("i"):
            camaras[camara_activa].cambiar_luz_led("IR")
        elif tecla == ord("o"):
            camaras[camara_activa].cambiar_luz_led("AUTO")

finally:
    print("Cerrando conexiones de las 4 cámaras...")
    for cam in camaras:
        if isinstance(cam, CamaraDVRIP):
            cam.cerrar()
        else:
            cam.detener = True
            cam.detener_audio()
            if cam.video_writer:
                cam.video_writer.release()
    time.sleep(0.5)
    cv2.destroyAllWindows()
