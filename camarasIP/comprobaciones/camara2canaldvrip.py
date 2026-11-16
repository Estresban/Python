import hashlib
import json
import os
import queue
import socket
import struct
import subprocess
import threading
import time
from datetime import datetime
import cv2
import numpy as np
import sounddevice as sd
from dvrip import DVRIPCam

# ==============================================================================
# GUÍA DE CONTROLES - CÁMARA DOBLE LENTE DVRIP
# ==============================================================================
# [RATÓN]      -> Clic en los botones "ESCUCHAR [V]" o "HABLAR [T]".
# [V]          -> Activar / Silenciar AUDIO de la cámara.
# [T]          -> Activar / Desactivar MICRÓFONO PC hacia la cámara.
# [W, A, S, D] -> Mover PTZ (Arriba / Izquierda / Abajo / Derecha).
# [+] / [-]    -> Zoom óptico PTZ (acercar / alejar).
# [Z] / [X]    -> Zoom digital en lente inferior (acercar / alejar).
# [L]          -> Encender LEDs de LUZ BLANCA (visión nocturna a color).
# [I]          -> Encender LEDs INFRARROJOS (visión nocturna en B/N).
# [O]          -> Poner iluminación en modo AUTOMÁTICO inteligente.
# [M]          -> ACTIVAR / DESACTIVAR detección de movimiento.
# [R]          -> ACTIVAR / DESACTIVAR grabación de video (.mp4).
# [F]          -> ACTIVAR / DESACTIVAR captura periódica de fotogramas.
# [C]          -> Tomar una CAPTURA DE FOTO manual.
# [Q]          -> Cerrar conexiones de forma segura y salir.
# ==============================================================================

CONFIG_CAMARA = {
    "nombre": "",
    "ip": "",
    "usuario": "",
    "password": "",
    "puerto_netip": 34567,
    "canales": (0, 1),  # 0 = lente inferior; 1 = lente superior
}

ANCHO = 640
ALTO_LENTE = 360  # Alto de cada lente individual (ventana total: 640x720)
ALTO_TOTAL = ALTO_LENTE * 2

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
# CLASE PRINCIPAL DE CÁMARA DVRIP COMPLETA
# ==============================================================================

class CamaraDVRIPCompleta:
    def __init__(self, cfg):
        self.cfg = cfg
        self.nombre = cfg["nombre"]
        self.detener = False
        self.conectada = False

        # Estados de funciones
        self.grabando = False
        self.deteccion_activa = False
        self.captura_auto_activa = False
        self.escuchando_audio = False
        self.hablando_micro = False
        self.movimiento_detectado = False
        self.modo_luz_actual = "Auto"
        self.zoom_digital = 1.0

        # Botones UI en la parte inferior de la ventana (640x720)
        self.btn_escuchar = (15, ALTO_TOTAL - 45, 155, ALTO_TOTAL - 12)
        self.btn_hablar = (165, ALTO_TOTAL - 45, 305, ALTO_TOTAL - 12)

        # Recursos de grabación y detección
        self.video_writer = None
        self.inicio_bloque = 0
        self.fondo_gris = None
        self.ultima_captura_mov = 0
        self.ultimo_fotograma_auto = 0

        # Recursos DVRIP y FFmpeg
        self.lock = threading.Lock()
        self.lock_control = threading.Lock()
        self.ultima_lente = {0: None, 1: None}
        self.frame_combinado = None

        self.colas_video = {0: queue.Queue(maxsize=100), 1: queue.Queue(maxsize=100)}
        self.cola_audio = queue.Queue(maxsize=100)
        self.procesos = {}
        self.logs = {}
        self.camaras_dvrip = {}
        self.cam_control = None

        self._iniciar_conexiones()

    def _iniciar_conexiones(self):
        # 1. Conexión dedicada para PTZ
        self.cam_control = DVRIPCam(
            self.cfg["ip"], user=self.cfg["usuario"], password=self.cfg["password"]
        )
        if self.cam_control.login():
            print(f"[{self.nombre}] Sesión de control PTZ iniciada.")
        else:
            print(f"[{self.nombre}] Aviso: No se pudo iniciar sesión PTZ.")

        # 2. Conexiones de vídeo por cada lente
        for canal in self.cfg["canales"]:
            cam = DVRIPCam(
                self.cfg["ip"], user=self.cfg["usuario"], password=self.cfg["password"]
            )
            if not cam.login():
                raise SystemExit(f"No se pudo conectar con la lente {canal}")
            self.camaras_dvrip[canal] = cam

            cmd = [
                "ffmpeg", "-loglevel", "error",
                "-f", "hevc", "-i", "pipe:0",
                "-an", "-vf", f"scale={ANCHO}:{ALTO_LENTE}",
                "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1"
            ]
            log = open(f"ffmpeg_lente_{canal}.log", "w")
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, bufsize=0
            )
            self.procesos[canal] = proc
            self.logs[canal] = log

            threading.Thread(target=self._alimentar_ffmpeg, args=(canal,), daemon=True).start()
            threading.Thread(target=self._leer_ffmpeg, args=(canal,), daemon=True).start()
            threading.Thread(
                target=cam.start_monitor,
                args=(self._crear_callback(canal), None),
                kwargs={"channel": canal},
                daemon=True
            ).start()

        self.conectada = True
        print(f"[{self.nombre}] Lentes 0 y 1 conectadas correctamente.")

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
            if paquete is None:
                break
            try:
                proc.stdin.write(paquete)
                proc.stdin.flush()
            except (BrokenPipeError, OSError):
                break

    def _leer_ffmpeg(self, canal):
        proc = self.procesos[canal]
        bytes_frame = ANCHO * ALTO_LENTE * 3
        buffer = bytearray()

        while not self.detener and proc.poll() is None:
            datos = proc.stdout.read(65536)
            if not datos:
                break
            buffer.extend(datos)

            while len(buffer) >= bytes_frame:
                raw = bytes(buffer[:bytes_frame])
                del buffer[:bytes_frame]
                img = np.frombuffer(raw, dtype=np.uint8).reshape((ALTO_LENTE, ANCHO, 3)).copy()

                with self.lock:
                    self.ultima_lente[canal] = img
                    inf = self.ultima_lente[0]
                    sup = self.ultima_lente[1]
                    if inf is not None and sup is not None:
                        self.frame_combinado = np.vstack((sup, inf))

    # ==========================================================================
    # CONTROL PTZ E ILUMINACIÓN (SOLUCIÓN CORREGIDA)
    # ==========================================================================

    def mover_ptz(self, direccion, duracion=0.35, velocidad=4, canal=0):
        def enviar_comando(preset_val):
            parametros = {
                "AUX": {"Number": 0, "Status": "On"},
                "Channel": canal,
                "MenuOpts": "Enter",
                "POINT": {"bottom": 0, "left": 0, "right": 0, "top": 0},
                "Pattern": "SetBegin",
                "Preset": preset_val,
                "Step": velocidad,
                "Tour": 0,
            }
            
            self.cam_control.set_command(
                "OPPTZControl", {"Command": direccion, "Parameter": parametros}
            )

        def ejecutar():
            with self.lock_control:
                try:
                    enviar_comando(65535)
                    time.sleep(duracion)
                    enviar_comando(-1)
                except Exception as e:
                    print(f"[{self.nombre}] Error PTZ ({direccion}): {e}")

        threading.Thread(target=ejecutar, daemon=True).start()

    def cambiar_luz_led(self, modo):
        """Envía el payload completo Camera.WhiteLight con WorkPeriod por puerto 34567."""
        self.modo_luz_actual = modo

        def _enviar_netip():
            mapa_workmode = {"BLANCA": "KeepOpen", "IR": "Close", "AUTO": "Auto"}
            work_mode = mapa_workmode.get(modo, "Auto")

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
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
                resp_login = sock.recv(1024)
                session_id = struct.unpack("<I", resp_login[4:8])[0] if len(resp_login) >= 8 else 0

                # 2. Configuración completa de luz blanca + horario
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

    # ==========================================================================
    # AUDIO BIDIRECCIONAL (ESCUCHAR Y HABLAR)
    # ==========================================================================

    def alternar_escuchar_audio(self):
        self.escuchando_audio = not self.escuchando_audio
        if self.escuchando_audio:
            while not self.cola_audio.empty():
                try:
                    self.cola_audio.get_nowait()
                except queue.Empty:
                    break
            threading.Thread(target=self._bucle_reproducir_audio, daemon=True).start()
        print(f"[{self.nombre}] Escucha de audio: {'ACTIVADA' if self.escuchando_audio else 'SILENCIADA'}")

    def _bucle_reproducir_audio(self):
        try:
            with sd.OutputStream(device=3, samplerate=8000, channels=1, dtype="int16") as salida:
                while self.escuchando_audio and not self.detener:
                    try:
                        pcm = self.cola_audio.get(timeout=0.2)
                        salida.write(pcm)
                    except queue.Empty:
                        continue
        except Exception as e:
            print(f"[{self.nombre}] Error salida audio: {e}")
        finally:
            self.escuchando_audio = False

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

            # 1. Login en socket dedicado
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





    # ==========================================================================
    # GRABACIÓN, MOVIMIENTO, CAPTURAS Y ZOOM DIGITAL
    # ==========================================================================

    def cambiar_zoom_digital(self, incremento):
        self.zoom_digital = max(1.0, min(4.0, self.zoom_digital + incremento))
        print(f"[{self.nombre}] Zoom digital lente inferior: {self.zoom_digital:.1f}x")

    def alternar_deteccion(self):
        self.deteccion_activa = not self.deteccion_activa
        if not self.deteccion_activa:
            self.movimiento_detectado = False
            self.fondo_gris = None
        print(f"[{self.nombre}] Detección movimiento: {'ON' if self.deteccion_activa else 'OFF'}")

    def alternar_grabacion(self):
        self.grabando = not self.grabando
        if not self.grabando and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            print(f"[{self.nombre}] Grabación DETENIDA y guardada.")
        elif self.grabando:
            print(f"[{self.nombre}] Grabación INICIADA.")

    def alternar_captura_auto(self):
        self.captura_auto_activa = not self.captura_auto_activa
        print(f"[{self.nombre}] Captura periódica: {'ON' if self.captura_auto_activa else 'OFF'}")

    def capturar_fotograma_manual(self):
        if self.frame_combinado is not None:
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            ruta = f"capturas_fotogramas/MANUAL_{self.nombre}_{fecha}.jpg"
            cv2.imwrite(ruta, self.frame_combinado)
            print(f"[{self.nombre}] Foto manual guardada -> {ruta}")

    def _aplicar_zoom_digital(self, frame):
        if self.zoom_digital <= 1.0:
            return frame
        parte_superior = frame[:ALTO_LENTE, :]
        parte_inferior = frame[ALTO_LENTE:, :]

        nh = int(ALTO_LENTE / self.zoom_digital)
        nw = int(ANCHO / self.zoom_digital)
        y1 = (ALTO_LENTE - nh) // 2
        x1 = (ANCHO - nw) // 2

        recorte = parte_inferior[y1:y1 + nh, x1:x1 + nw]
        parte_inferior_zoom = cv2.resize(recorte, (ANCHO, ALTO_LENTE))
        return np.vstack((parte_superior, parte_inferior_zoom))

    def _procesar_analitica(self, frame):
        ahora = time.time()

        # 1. Detección de movimiento
        if self.deteccion_activa:
            gris = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            if self.fondo_gris is None:
                self.fondo_gris = gris
            else:
                diff = cv2.absdiff(self.fondo_gris, gris)
                _, umbral = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                umbral = cv2.dilate(umbral, None, iterations=2)
                contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                self.movimiento_detectado = any(
                    cv2.contourArea(c) > SENSIBILIDAD_MOVIMIENTO for c in contornos
                )
                self.fondo_gris = cv2.addWeighted(self.fondo_gris, 0.95, gris, 0.05, 0)

                if self.movimiento_detectado and (ahora - self.ultima_captura_mov) >= COOLDOWN_CAPTURA_SEG:
                    self.ultima_captura_mov = ahora
                    ruta = f"capturas_movimiento/MOV_{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
                    cv2.imwrite(ruta, frame)
                    print(f"¡ALERTA! Movimiento en {self.nombre} -> {ruta}")

        # 2. Grabación MP4 en bloques
        if self.grabando:
            if self.video_writer is None or (ahora - self.inicio_bloque) >= (MINUTOS_POR_BLOQUE_VIDEO * 60):
                if self.video_writer:
                    self.video_writer.release()
                ruta = f"grabaciones/{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                self.video_writer = cv2.VideoWriter(ruta, fourcc, 20.0, (ANCHO, ALTO_TOTAL))
                self.inicio_bloque = ahora
            self.video_writer.write(frame)
            gris = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            if self.fondo_gris is None:
                self.fondo_gris = gris
            else:
                diff = cv2.absdiff(self.fondo_gris, gris)
                _, umbral = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                umbral = cv2.dilate(umbral, None, iterations=2)
                contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                self.movimiento_detectado = any(
                    cv2.contourArea(c) > SENSIBILIDAD_MOVIMIENTO for c in contornos
                )
                self.fondo_gris = cv2.addWeighted(self.fondo_gris, 0.95, gris, 0.05, 0)

                if self.movimiento_detectado and (ahora - self.ultima_captura_mov) >= COOLDOWN_CAPTURA_SEG:
                    self.ultima_captura_mov = ahora
                    ruta = f"capturas_movimiento/MOV_{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
                    cv2.imwrite(ruta, frame)
                    print(f"¡ALERTA! Movimiento en {self.nombre} -> {ruta}")

        # 2. Grabación MP4 en bloques
        if self.grabando:
            if self.video_writer is None or (ahora - self.inicio_bloque) >= (MINUTOS_POR_BLOQUE_VIDEO * 60):
                if self.video_writer:
                    self.video_writer.release()
                ruta = f"grabaciones/{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                self.video_writer = cv2.VideoWriter(ruta, fourcc, 20.0, (ANCHO, ALTO_TOTAL))
                self.inicio_bloque = ahora
            self.video_writer.write(frame)
        # 3. Captura periódica
        if self.captura_auto_activa and (ahora - self.ultimo_fotograma_auto) >= INTERVALO_FOTOGRAMA_AUTO_SEG:
            self.ultimo_fotograma_auto = ahora
            ruta = f"capturas_fotogramas/AUTO_{self.nombre}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
            cv2.imwrite(ruta, frame)
            print(f"[{self.nombre}] Fotograma periódico guardado -> {ruta}")

    def obtener_imagen_ui(self):
        with self.lock:
            base = self.frame_combinado.copy() if self.frame_combinado is not None else None

        if base is None:
            img = np.zeros((ALTO_TOTAL, ANCHO, 3), dtype=np.uint8)
            cv2.putText(
                img, f"{self.nombre}: Esperando ambas lentes DVRIP...",
                (90, ALTO_TOTAL // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )
            return img

        self._procesar_analitica(base)
        img = self._aplicar_zoom_digital(base)

        # Barra superior izquierda
        titulo = f"{self.nombre} | Z:{self.zoom_digital:.1f}x | Luz:{self.modo_luz_actual}"
        cv2.putText(img, titulo, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        # Indicadores superiores derechos
        color_mov = (0, 255, 0) if self.deteccion_activa else (140, 140, 140)
        cv2.putText(img, f"MOV:{'ON' if self.deteccion_activa else 'OFF'}", (415, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_mov, 2)

        color_fot = (0, 255, 255) if self.captura_auto_activa else (140, 140, 140)
        cv2.putText(img, f"FOT:{'ON' if self.captura_auto_activa else 'OFF'}", (495, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_fot, 2)

        if self.grabando:
            cv2.circle(img, (582, 19), 6, (0, 0, 255), -1)
            cv2.putText(img, "REC", (592, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 255), 2)

        # Botones clicables inferiores
        for rect, activo, txt_on, txt_off in (
            (self.btn_escuchar, self.escuchando_audio, "OYENDO [V]", "ESCUCHAR [V]"),
            (self.btn_hablar, self.hablando_micro, "HABLANDO [T]", "HABLAR [T]"),
        ):
            x1, y1, x2, y2 = rect
            color = (200, 130, 0) if (activo and rect == self.btn_escuchar) else (
                (0, 0, 220) if activo else (55, 55, 55)
            )
            cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)
            cv2.putText(img, txt_on if activo else txt_off, (x1 + 8, y1 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)

        # Marco de alerta por movimiento
        if self.movimiento_detectado:
            cv2.rectangle(img, (3, 3), (ANCHO - 3, ALTO_TOTAL - 3), (0, 0, 255), 4)
            cv2.putText(img, "MOVIMIENTO DETECTADO", (415, ALTO_TOTAL - 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 255), 2)

        return img

    def cerrar(self):
        self.detener = True
        self.escuchando_audio = False
        self.hablando_micro = False

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
                proc.kill()

        for log in self.logs.values():
            try:
                log.close()
            except Exception:
                pass

        if self.video_writer:
            self.video_writer.release()


# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

camara = CamaraDVRIPCompleta(CONFIG_CAMARA)
NOMBRE_VENTANA = f"Control Completo - {CONFIG_CAMARA['nombre']} ({CONFIG_CAMARA['ip']})"

def gestionar_clic_raton(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1, x2, y2 = camara.btn_escuchar
        if x1 <= x <= x2 and y1 <= y <= y2:
            camara.alternar_escuchar_audio()
            return
        x1, y1, x2, y2 = camara.btn_hablar
        if x1 <= x <= x2 and y1 <= y <= y2:
            camara.alternar_hablar_micro()

cv2.namedWindow(NOMBRE_VENTANA)
cv2.setMouseCallback(NOMBRE_VENTANA, gestionar_clic_raton)

print("\n=== CONTROL DE CÁMARA DOBLE LENTE INICIADO ===")
print("WASD: PTZ | +/-: Zoom óptico | Z/X: Zoom digital | L/I/O: Luz Blanca/IR/Auto")
print("V: Escuchar | T: Hablar | M: Movimiento | R: Grabar | F: Fotos auto | C: Foto | Q: Salir\n")

try:
    while True:
        cv2.imshow(NOMBRE_VENTANA, camara.obtener_imagen_ui())
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("q"):
            break
        elif tecla == ord("w"):
            camara.mover_ptz("DirectionUp")
        elif tecla == ord("s"):
            camara.mover_ptz("DirectionDown")
        elif tecla == ord("a"):
            camara.mover_ptz("DirectionLeft")
        elif tecla == ord("d"):
            camara.mover_ptz("DirectionRight")
        elif tecla in (ord("+"), ord("=")):
            camara.mover_ptz("ZoomTile")
        elif tecla == ord("-"):
            camara.mover_ptz("ZoomWide")
        elif tecla == ord("z"):
            camara.cambiar_zoom_digital(0.2)
        elif tecla == ord("x"):
            camara.cambiar_zoom_digital(-0.2)
        elif tecla == ord("l"):
            camara.cambiar_luz_led("BLANCA")
        elif tecla == ord("i"):
            camara.cambiar_luz_led("IR")
        elif tecla == ord("o"):
            camara.cambiar_luz_led("AUTO")
        elif tecla == ord("v"):
            camara.alternar_escuchar_audio()
        elif tecla == ord("t"):
            camara.alternar_hablar_micro()
        elif tecla == ord("m"):
            camara.alternar_deteccion()
        elif tecla == ord("r"):
            camara.alternar_grabacion()
        elif tecla == ord("f"):
            camara.alternar_captura_auto()
        elif tecla == ord("c"):
            camara.capturar_fotograma_manual()

finally:
    print("Cerrando conexiones y liberando recursos...")
    camara.cerrar()
    cv2.destroyAllWindows()
