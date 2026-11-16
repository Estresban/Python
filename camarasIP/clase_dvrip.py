from datetime import datetime
import json
import queue
import socket
import struct
import subprocess
import threading
import time
import cv2
from dvrip import DVRIPCam
import numpy as np
import sounddevice as sd
from notificaciones import enviar_alerta_movimiento

from config import (
    ALTO_CELDA,
    ALTO_LENTE_DVRIP,
    ANCHO_CELDA,
    COOLDOWN_CAPTURA_SEG,
    DISPOSITIVO_SALIDA_AUDIO,
    INTERVALO_FOTOGRAMA_AUTO_SEG,
    MINUTOS_POR_BLOQUE_VIDEO,
    SENSIBILIDAD_MOVIMIENTO,
    alaw_a_pcm,
    hash_xmeye,
    pcm16_a_alaw,
)


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
                threading.Thread(target=self._bucle_monitor_dvrip, args=(canal,), daemon=True).start()

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
                    # Canal 1 = lente superior
                    # Canal 0 = lente inferior
                    self.ultima_lente[canal] = img

                    lente_superior = self.ultima_lente.get(1)
                    lente_inferior = self.ultima_lente.get(0)

                    # Esperar a recibir las dos imágenes
                    if lente_superior is not None and lente_inferior is not None:

                        self.frame = np.vstack(
                            (lente_superior, lente_inferior)
                        ).astype(np.uint8, copy=False)
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
            with sd.OutputStream(
                device=DISPOSITIVO_SALIDA_AUDIO, samplerate=8000, channels=1, dtype="int16"
            ) as out:
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
                    enviar_alerta_movimiento(frame, self.nombre)

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
        '''
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
