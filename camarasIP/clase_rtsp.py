from datetime import datetime
import json
import os
import socket
import struct
import subprocess
import threading
import time
import cv2
import numpy as np
from onvif import ONVIFCamera
import sounddevice as sd
from notificaciones import enviar_alerta_movimiento

from config import (
    ALTO_CELDA,
    ANCHO_CELDA,
    COOLDOWN_CAPTURA_SEG,
    INTERVALO_FOTOGRAMA_AUTO_SEG,
    MINUTOS_POR_BLOQUE_VIDEO,
    SENSIBILIDAD_MOVIMIENTO,
    hash_xmeye,
    pcm16_a_alaw,
)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"


class CamaraAvanzada:
    """Controla cámaras IP mediante RTSP (vídeo/audio), ONVIF (PTZ) y NetIP (LED/Voz)."""

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
                nombres_limpios = {
                    "BLANCA": "Luz blanca",
                    "IR": "IR",
                    "AUTO": "Auto",
                }
                etiqueta = nombres_limpios.get(modo, modo)

                if '"Ret" : 100' in texto_resp or '"Ret": 100' in texto_resp:
                    print(f"[{self.nombre}] Iluminación: {etiqueta}")
                else:
                    print(f"[{self.nombre}] No se pudo cambiar la luz a {etiqueta}")

            except Exception as e:
                print(f"[{self.nombre}] Error conectando al puerto 34567: {e}")

        threading.Thread(target=_enviar_comando_netip, daemon=True).start()


    # --- AUDIO BIDIRECCIONAL ---
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

    # --- DETECCIÓN, GRABACIÓN Y CAPTURAS ---
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
                enviar_alerta_movimiento(frame, self.nombre)
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
        '''
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
        '''
        if self.movimiento_detectado:
            cv2.rectangle(img, (3, 3), (ANCHO_CELDA - 3, ALTO_CELDA - 3), (0, 0, 255), 4)
            cv2.putText(img, "MOVIMIENTO DETECTADO", (415, 342), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 255), 2)
        elif seleccionada:
            cv2.rectangle(img, (2, 2), (ANCHO_CELDA - 2, ALTO_CELDA - 2), (0, 255, 255), 3)

        return img

    def cerrar(self):
        self.detener = True
        self.detener_audio()
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
