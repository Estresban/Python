"""
main.py
Interfaz principal para las cámaras RTSP y DVRIP.

Estructura esperada:
    main.py
    config.py
    camara_rtsp.py
    camara_dvrip.py

Controles:
    Ratón       Seleccionar cámara / pulsar los botones dibujados
    Flechas     Mover PTZ de la cámara seleccionada
    + / -       Zoom digital
    M           Detección de movimiento
    R           Grabación
    F           Captura automática
    Espacio     Fotografía manual
    V           Escuchar audio
    T           Hablar por el micrófono del PC
    1 / 2 / 3   Luz blanca / infrarrojos / automático
    Esc / Q     Salir
"""

import os
import sys
import threading
import time
import math
import numpy as np

from config import (
    RUTA_BASE,
    DIR_DATOS,
    CONFIG_CAMARAS_RTSP,
    CONFIG_PATIO,
    ANCHO_CELDA,
    ALTO_CELDA,
    ANCHO_TOTAL_BASE,
    ALTO_TOTAL_BASE,
    CARPETAS_SALIDA,
)

# 1. Evita que FFmpeg / OpenCV creen archivos .log sueltos o muestren ruido innecesario
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"  # Silencia logs de FFmpeg (AV_LOG_QUIET)
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"     # Solo errores críticos en OpenCV

# 2. Fuerza que cualquier archivo temporal o log residual se cree dentro de camarasIP
os.chdir(DIR_DATOS)

import cv2
import configuracion
from clase_rtsp import CamaraAvanzada
from clase_dvrip import CamaraDVRIP
import notificaciones


VENTANA = "Sistema de videovigilancia"
ANCHO_PANEL = 360
CAMARAS = []
seleccionada = 0


def preparar_carpetas():
    """Crea las carpetas usadas por las clases antes de guardar archivos."""
    for carpeta in CARPETAS_SALIDA:
        os.makedirs(carpeta, exist_ok=True)


def iniciar_camaras():
    """Crea las tres cámaras RTSP y la cámara DVRIP del patio."""
    camaras = []

    for indice, cfg in enumerate(CONFIG_CAMARAS_RTSP):
        try:
            print(f"[MAIN] Iniciando cámara RTSP: {cfg['nombre']}")
            camaras.append(CamaraAvanzada(cfg, indice))
        except Exception as exc:
            print(f"[MAIN] No se pudo iniciar {cfg.get('nombre', indice)}: {exc}")

    try:
        indice = len(camaras)
        print(f"[MAIN] Iniciando cámara DVRIP: {CONFIG_PATIO['nombre']}")
        camaras.append(CamaraDVRIP(CONFIG_PATIO, indice))
    except Exception as exc:
        print(f"[MAIN] No se pudo iniciar Patio: {exc}")

    return camaras


def dibujar_interfaz(camaras, indice_activo):
    """Compone la cuadrícula 2x2 con la imagen de cada cámara."""
    lienzo = np.zeros((ALTO_TOTAL_BASE, ANCHO_TOTAL_BASE, 3), dtype=np.uint8)

    for indice in range(4):
        x = (indice % 2) * ANCHO_CELDA
        y = (indice // 2) * ALTO_CELDA

        if indice < len(camaras):
            try:
                imagen = camaras[indice].obtener_imagen_ui(
                    seleccionada=(indice == indice_activo)
                )
            except Exception as exc:
                imagen = np.zeros((ALTO_CELDA, ANCHO_CELDA, 3), dtype=np.uint8)
                cv2.putText(
                    imagen, f"Error mostrando cámara: {exc}",
                    (15, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 1, cv2.LINE_AA
                )
        else:
            imagen = np.zeros((ALTO_CELDA, ANCHO_CELDA, 3), dtype=np.uint8)
            cv2.putText(
                imagen, "Sin cámara configurada", (150, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 130, 130), 2
            )

        if imagen.shape[1] != ANCHO_CELDA or imagen.shape[0] != ALTO_CELDA:
            imagen = cv2.resize(imagen, (ANCHO_CELDA, ALTO_CELDA))

        lienzo[y:y + ALTO_CELDA, x:x + ANCHO_CELDA] = imagen

        # Separadores de la cuadrícula.
        cv2.rectangle(
            lienzo, (x, y), (x + ANCHO_CELDA - 1, y + ALTO_CELDA - 1),
            (75, 75, 75), 1
        )

    return lienzo


def alternar_metodo(camara, nombre):
    metodo = getattr(camara, nombre, None)
    if callable(metodo):
        metodo()
    else:
        print(f"[MAIN] La cámara {camara.nombre} no implementa {nombre}().")


def controlar_camara(camara, tecla):
    """Aplica una tecla a la cámara seleccionada."""
    
    # Control PTZ con W, A, S, D (con el eje horizontal ya corregido)
    if tecla in (ord("w"), ord("W")):
        camara.mover_ptz(0.0, 0.5, 0.0)   # arriba
        return

    elif tecla in (ord("a"), ord("A")):
        camara.mover_ptz(0.0, -0.5, 0.0)  # abajo
        return

    elif tecla in (ord("s"), ord("S")):
        camara.mover_ptz(0.5, 0.0, 0.0)   # izquierda
        return

    elif tecla in (ord("d"), ord("D")):
        camara.mover_ptz(-0.5, 0.0, 0.0)  # derecha
        return
    
    if tecla in (ord("m"), ord("M")):
        alternar_metodo(camara, "alternar_deteccion")

    elif tecla in (ord("r"), ord("R")):
        alternar_metodo(camara, "alternar_grabacion")

    elif tecla in (ord("f"), ord("F")):
        alternar_metodo(camara, "alternar_captura_auto")

    elif tecla == ord(" "):
        alternar_metodo(camara, "capturar_fotograma_manual")

    elif tecla in (ord("v"), ord("V")):
        alternar_metodo(camara, "alternar_escuchar_audio")

    elif tecla in (ord("t"), ord("T")):
        alternar_metodo(camara, "alternar_hablar_micro")

    elif tecla in (ord("+"), ord("Z"), ord("z")):
        alternar_zoom(camara, 0.2)

    elif tecla in (ord("-"), ord("X"), ord("x")):
        alternar_zoom(camara, -0.2)

    elif tecla in (ord("1"), ord("L"), ord("l")):
        camara.cambiar_luz_led("BLANCA")

    elif tecla in (ord("2"), ord("I"), ord("i")):
        camara.cambiar_luz_led("IR")

    elif tecla in (ord("3"), ord("O"), ord("o")):
        camara.cambiar_luz_led("AUTO")
    
    elif tecla in (ord("n"), ord("N")):
        notificaciones.alternar_alertas()


def alternar_zoom(camara, incremento):
    metodo = getattr(camara, "cambiar_zoom", None)
    if callable(metodo):
        metodo(incremento)


FLECHAS_IZQ = (81, 65361, 2424832)
FLECHAS_ARR = (82, 65362, 2490368)
FLECHAS_DER = (83, 65363, 2555904)
FLECHAS_ABA = (84, 65364, 2621440)
TODAS_LAS_FLECHAS = FLECHAS_IZQ + FLECHAS_ARR + FLECHAS_DER + FLECHAS_ABA


def mover_ptz(camara, tecla):
    """Movimiento breve PTZ con las flechas del teclado (Windows y Linux)."""
    if tecla in FLECHAS_IZQ:
        camara.mover_ptz(0.5, 0.0, 0.0)   # izquierda (corregida)
    elif tecla in FLECHAS_ARR:
        camara.mover_ptz(0.0, 0.5, 0.0)   # arriba
    elif tecla in FLECHAS_DER:
        camara.mover_ptz(-0.5, 0.0, 0.0)  # derecha (corregida)
    elif tecla in FLECHAS_ABA:
        camara.mover_ptz(0.0, -0.5, 0.0)  # abajo


def al_hacer_clic(evento, x, y, flags, parametros):
    """Selecciona una celda de cámara."""
    global seleccionada
    camaras = parametros

    if evento != cv2.EVENT_LBUTTONDOWN:
        return

    columna = 0 if x < ANCHO_CELDA else 1
    fila = 0 if y < ALTO_CELDA else 1
    indice = fila * 2 + columna

    if indice >= len(camaras):
        return

    seleccionada = indice
    camara = camaras[indice]




# ---------------------------------------------------------------------
# Panel gráfico de control
# ---------------------------------------------------------------------

BOTONES_PANEL = [
    # texto, x1, y1, x2, y2, acción
    ("ARRIBA",       105,  82, 255, 122, "arriba"),
    ("IZQUIERDA",     15, 128, 165, 168, "izquierda"),
    ("DERECHA",      195, 128, 345, 168, "derecha"),
    ("ABAJO",        105, 174, 255, 214, "abajo"),
    ("ZOOM  +",            15, 232, 165, 276, "zoom_mas"),
    ("ZOOM  -",           195, 232, 345, 276, "zoom_menos"),
    ("DETECCIÓN",          15, 298, 165, 342, "deteccion"),
    ("GRABACIÓN",         195, 298, 345, 342, "grabacion"),
    ("CAPTURA AUTO",       15, 354, 165, 398, "captura_auto"),
    ("FOTO MANUAL",       195, 354, 345, 398, "foto"),
    ("ESCUCHAR AUDIO",     15, 410, 165, 454, "audio"),
    ("MICRÓFONO",         195, 410, 345, 454, "micro"),
    ("LUZ BLANCA",         15, 478, 120, 522, "luz_blanca"),
    ("INFRARROJOS",       130, 478, 245, 522, "luz_ir"),
    ("LUZ AUTO",          255, 478, 345, 522, "luz_auto"),
    ("ALERTAS MOVIL",       15, 555, 175, 605, "alertas"),
    ("CONFIGURACION",      185, 555, 345, 605, "configuracion"),
    ("CERRAR",              15, 660, 345, 710, "salir"),
]


def dibujar_icono(panel, accion, cx, cy, activo):
    """Dibuja iconos vectoriales limpios usando primitivas de OpenCV."""
    blanco = (255, 255, 255)
    rojo_tachado = (80, 80, 255)

    if accion in ("arriba", "abajo", "izquierda", "derecha"):
        # Flechas direccionales PTZ
        d = 9
        if accion == "arriba":
            pts = np.array([[cx, cy - d], [cx - d, cy + d - 3], [cx + d, cy + d - 3]])
        elif accion == "abajo":
            pts = np.array([[cx, cy + d], [cx - d, cy - d + 3], [cx + d, cy - d + 3]])
        elif accion == "izquierda":
            pts = np.array([[cx - d, cy], [cx + d - 3, cy - d], [cx + d - 3, cy + d]])
        else:  # derecha
            pts = np.array([[cx + d, cy], [cx - d + 3, cy - d], [cx - d + 3, cy + d]])
        cv2.fillPoly(panel, [pts], blanco, cv2.LINE_AA)

    elif accion in ("zoom_mas", "zoom_menos"):
        # Lupa con + o -
        cv2.circle(panel, (cx - 2, cy - 2), 7, blanco, 2, cv2.LINE_AA)
        cv2.line(panel, (cx + 3, cy + 3), (cx + 9, cy + 9), blanco, 2, cv2.LINE_AA)
        cv2.line(panel, (cx - 5, cy - 2), (cx + 1, cy - 2), blanco, 2, cv2.LINE_AA)
        if accion == "zoom_mas":
            cv2.line(panel, (cx - 2, cy - 5), (cx - 2, cy + 1), blanco, 2, cv2.LINE_AA)

    elif accion == "deteccion":
        # Ojo / sensor de movimiento
        cv2.ellipse(panel, (cx, cy), (11, 6), 0, 0, 360, blanco, 2, cv2.LINE_AA)
        cv2.circle(panel, (cx, cy), 3, blanco, -1, cv2.LINE_AA)

    elif accion == "grabacion":
        # Círculo REC
        color_rec = (255, 255, 255) if activo else (180, 180, 220)
        cv2.circle(panel, (cx, cy), 7, color_rec, -1, cv2.LINE_AA)
        cv2.circle(panel, (cx, cy), 10, blanco, 1, cv2.LINE_AA)

    elif accion in ("captura_auto", "foto"):
        # Cámara fotográfica
        cv2.rectangle(panel, (cx - 10, cy - 5), (cx + 10, cy + 7), blanco, 2, cv2.LINE_AA)
        cv2.rectangle(panel, (cx - 4, cy - 8), (cx + 4, cy - 5), blanco, -1, cv2.LINE_AA)
        cv2.circle(panel, (cx, cy + 1), 3, blanco, 2, cv2.LINE_AA)

    elif accion == "audio":
        # Altavoz
        pts = np.array([[cx - 9, cy - 3], [cx - 4, cy - 3], [cx + 2, cy - 8],
                        [cx + 2, cy + 8], [cx - 4, cy + 3], [cx - 9, cy + 3]])
        cv2.fillPoly(panel, [pts], blanco, cv2.LINE_AA)
        if activo:
            cv2.ellipse(panel, (cx + 3, cy), (4, 6), 0, -60, 60, blanco, 2, cv2.LINE_AA)
            cv2.ellipse(panel, (cx + 3, cy), (8, 10), 0, -60, 60, blanco, 2, cv2.LINE_AA)

    elif accion == "micro":
        # Micrófono
        cv2.rectangle(panel, (cx - 3, cy - 9), (cx + 3, cy + 1), blanco, -1, cv2.LINE_AA)
        cv2.ellipse(panel, (cx, cy), (6, 6), 0, 0, 180, blanco, 2, cv2.LINE_AA)
        cv2.line(panel, (cx, cy + 6), (cx, cy + 10), blanco, 2, cv2.LINE_AA)
        cv2.line(panel, (cx - 5, cy + 10), (cx + 5, cy + 10), blanco, 2, cv2.LINE_AA)

    elif accion.startswith("luz_"):
        # Bombilla
        cv2.circle(panel, (cx, cy - 3), 6, blanco, 2 if not activo else -1, cv2.LINE_AA)
        cv2.rectangle(panel, (cx - 3, cy + 3), (cx + 3, cy + 7), blanco, -1, cv2.LINE_AA)
        if activo:
            for ang in (-45, 0, 45, 135, 180, 225):
                rad = math.radians(ang)
                cv2.line(panel, (int(cx + 8 * math.cos(rad)), int(cy - 3 + 8 * math.sin(rad))),
                         (int(cx + 11 * math.cos(rad)), int(cy - 3 + 11 * math.sin(rad))), blanco, 1, cv2.LINE_AA)

    elif accion == "configuracion":
        # Rueda dentada (engranaje)
        cv2.circle(panel, (cx, cy), 6, blanco, 2, cv2.LINE_AA)
        cv2.circle(panel, (cx, cy), 2, blanco, -1, cv2.LINE_AA)
        for i in range(8):
            ang = math.radians(i * 45)
            x_in, y_in = int(cx + 6 * math.cos(ang)), int(cy + 6 * math.sin(ang))
            x_out, y_out = int(cx + 9 * math.cos(ang)), int(cy + 9 * math.sin(ang))
            cv2.line(panel, (x_in, y_in), (x_out, y_out), blanco, 2, cv2.LINE_AA)
    
    elif accion == "alertas":
        # Campana de notificación
        cv2.ellipse(panel, (cx, cy + 2), (7, 9), 0, 180, 360, blanco, -1, cv2.LINE_AA)
        cv2.line(panel, (cx - 9, cy + 3), (cx + 9, cy + 3), blanco, 2, cv2.LINE_AA)
        cv2.circle(panel, (cx, cy + 6), 2, blanco, -1, cv2.LINE_AA)

    elif accion == "salir":
        # Símbolo de cerrar (X)
        cv2.line(panel, (cx - 7, cy - 7), (cx + 7, cy + 7), blanco, 2, cv2.LINE_AA)
        cv2.line(panel, (cx + 7, cy - 7), (cx - 7, cy + 7), blanco, 2, cv2.LINE_AA)

    # Tachado visual cuando los interruptores de estado están apagados
    botones_con_tachado = ("audio", "micro", "deteccion", "grabacion", "captura_auto", "alertas")
    if accion in botones_con_tachado and not activo:
        cv2.line(panel, (cx - 11, cy - 11), (cx + 11, cy + 11), rojo_tachado, 2, cv2.LINE_AA)


# Variable global para rastrear la posición del ratón en el panel
raton_panel = (-1, -1)


def dibujar_boton_redondeado(img, x1, y1, x2, y2, radio, color_fondo, color_borde, grosor=1):
    """Dibuja un rectángulo con esquinas redondeadas usando primitivas de OpenCV."""
    # Relleno interior (cruz central)
    cv2.rectangle(img, (x1 + radio, y1), (x2 - radio, y2), color_fondo, -1)
    cv2.rectangle(img, (x1, y1 + radio), (x2, y2 - radio), color_fondo, -1)

    # 4 círculos rellenos para las esquinas
    esquinas = [
        (x1 + radio, y1 + radio, 180, 270),
        (x2 - radio, y1 + radio, 270, 360),
        (x2 - radio, y2 - radio, 0, 90),
        (x1 + radio, y2 - radio, 90, 180),
    ]
    for cx, cy, ang_ini, ang_fin in esquinas:
        cv2.circle(img, (cx, cy), radio, color_fondo, -1, cv2.LINE_AA)
        if color_borde is not None:
            cv2.ellipse(img, (cx, cy), (radio, radio), 0, ang_ini, ang_fin,
                        color_borde, grosor, cv2.LINE_AA)

    # Líneas rectas del borde
    if color_borde is not None:
        cv2.line(img, (x1 + radio, y1), (x2 - radio, y1), color_borde, grosor, cv2.LINE_AA)
        cv2.line(img, (x1 + radio, y2), (x2 - radio, y2), color_borde, grosor, cv2.LINE_AA)
        cv2.line(img, (x1, y1 + radio), (x1, y2 - radio), color_borde, grosor, cv2.LINE_AA)
        cv2.line(img, (x2, y1 + radio), (x2, y2 - radio), color_borde, grosor, cv2.LINE_AA)


def dibujar_panel(indice_activo, camaras):
    """Crea el panel lateral con botones redondeados, iconos y efecto hover."""
    panel = np.full((ALTO_TOTAL_BASE, ANCHO_PANEL, 3), 34, dtype=np.uint8)

    cv2.putText(panel, "PANEL DE CONTROL", (22, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.78, (245, 245, 245), 2, cv2.LINE_AA)
    cantidad_camaras = len(camaras)
    cv2.putText(panel, f"Camara seleccionada: {indice_activo + 1}/{cantidad_camaras}",
                (18, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.43,
                (180, 220, 255), 1, cv2.LINE_AA)

    camara = camaras[indice_activo] if camaras and indice_activo < len(camaras) else None

    estados = {}
    if camara is not None:
        modo_luz = str(getattr(camara, "modo_luz_actual", "AUTO")).upper()
        estados = {
            "deteccion": bool(getattr(camara, "deteccion_activa", False)),
            "grabacion": bool(getattr(camara, "grabando", False)),
            "captura_auto": bool(getattr(camara, "captura_auto_activa", False)),
            "audio": bool(getattr(camara, "escuchando_audio", False)),
            "micro": bool(getattr(camara, "hablando_micro", False)),
            "luz_blanca": modo_luz in ("BLANCA", "WHITE"),
            "luz_ir": modo_luz in ("IR", "INFRARROJA", "INFRARROJOS"),
            "luz_auto": modo_luz in ("AUTO", "AUTOMATICO", "AUTOMÁTICO"),
        }
    estados["alertas"] = notificaciones.alertas_activas

    etiquetas_visuales = {
        "zoom_mas": "ZOOM +",
        "zoom_menos": "ZOOM -",
        "luz_blanca": "BLANCA",
        "luz_ir": "IR",
        "luz_auto": "AUTO",
        "audio": "AUDIO",
        "micro": "MICRO",
        "deteccion": "DETECCION",
        "grabacion": "GRABAR",
        "captura_auto": "AUTO FOTO",
        "foto": "FOTO",
        "alertas": "ALERTAS",
        "configuracion": "AJUSTES",

    }

    mx, my = raton_panel
    radio_esquina = 10

    for texto, x1, y1, x2, y2, accion in BOTONES_PANEL:
        activo = estados.get(accion, False)
        encima = (x1 <= mx <= x2) and (y1 <= my <= y2)

        # Paleta de colores base
        color = (58, 72, 88)
        if activo:
            color = (40, 150, 55)
        if accion == "salir":
            color = (45, 50, 175)
        elif accion.startswith("luz_") and not activo:
            color = (68, 82, 62)

        # Efecto Hover: aclarar el fondo y resaltar el borde en blanco
        if encima:
            color = tuple(min(255, c + 30) for c in color)
            borde = (255, 255, 255)
            grosor_borde = 2
        else:
            borde = (120, 230, 130) if activo else (130, 140, 155)
            grosor_borde = 1

        # Sombra redondeada y botón principal redondeado
        dibujar_boton_redondeado(panel, x1 + 2, y1 + 3, x2 + 2, y2 + 3,
                                 radio_esquina, (20, 20, 20), None)
        dibujar_boton_redondeado(panel, x1, y1, x2, y2,
                                 radio_esquina, color, borde, grosor_borde)

        # Botones PTZ: flecha grande centrada
        if accion in ("arriba", "abajo", "izquierda", "derecha"):
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            dibujar_icono(panel, accion, cx, cy, True)
            continue

        # Resto de botones: icono + texto
        icono_x = x1 + 20
        icono_y = (y1 + y2) // 2
        dibujar_icono(panel, accion, icono_x, icono_y, activo)

        texto_mostrar = etiquetas_visuales.get(accion, texto)
        escala = 0.42 if len(texto_mostrar) > 9 else 0.48
        tam, _ = cv2.getTextSize(texto_mostrar, cv2.FONT_HERSHEY_SIMPLEX, escala, 1)

        zona_texto_x1 = x1 + 36
        tx = zona_texto_x1 + max(2, (x2 - zona_texto_x1 - tam[0]) // 2)
        ty = y1 + (y2 - y1 + tam[1]) // 2
        cv2.putText(panel, texto_mostrar, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX,
                    escala, (255, 255, 255), 1, cv2.LINE_AA)

    #cv2.putText(panel, "Teclado: flechas PTZ | +/- zoom | M deteccion", (18, 635),
    #            cv2.FONT_HERSHEY_SIMPLEX, 0.31, (190, 190, 190), 1, cv2.LINE_AA)
    return panel

ventana_config_abierta = False


def abrir_configuracion_hilo():
    """Abre la ventana Tkinter sin bloquear el vídeo ni usar subprocess."""
    global ventana_config_abierta
    if ventana_config_abierta:
        return
    ventana_config_abierta = True
    try:
        configuracion.iniciar()
    except Exception as exc:
        print(f"[CONFIG] Error en ventana de configuración: {exc}")
    finally:
        ventana_config_abierta = False


def ejecutar_accion_panel(accion, camaras):
    """Ejecuta la acción del botón sobre la cámara actualmente seleccionada."""
    global seleccionada
    if accion == "salir":
        return False
    if accion == "alertas":
        notificaciones.alternar_alertas()
        return True

    if accion == "configuracion":
        threading.Thread(target=abrir_configuracion_hilo, daemon=True).start()
        return True
    if not camaras or seleccionada >= len(camaras):
        return True

    camara = camaras[seleccionada]
    acciones = {
        "arriba": lambda: camara.mover_ptz(0, 0.5, 0),
        "abajo": lambda: camara.mover_ptz(0, -0.5, 0),
        "izquierda": lambda: camara.mover_ptz(0.5, 0, 0),
        "derecha": lambda: camara.mover_ptz(-0.5, 0, 0),
        "zoom_mas": lambda: alternar_zoom(camara, 0.2),
        "zoom_menos": lambda: alternar_zoom(camara, -0.2),
        "deteccion": lambda: alternar_metodo(camara, "alternar_deteccion"),
        "grabacion": lambda: alternar_metodo(camara, "alternar_grabacion"),
        "captura_auto": lambda: alternar_metodo(camara, "alternar_captura_auto"),
        "foto": lambda: alternar_metodo(camara, "capturar_fotograma_manual"),
        "audio": lambda: alternar_metodo(camara, "alternar_escuchar_audio"),
        "micro": lambda: alternar_metodo(camara, "alternar_hablar_micro"),
        "luz_blanca": lambda: camara.cambiar_luz_led("BLANCA"),
        "luz_ir": lambda: camara.cambiar_luz_led("IR"),
        "luz_auto": lambda: camara.cambiar_luz_led("AUTO"),
    }
    try:
        funcion = acciones.get(accion)
        if funcion:
            funcion()
    except Exception as exc:
        print(f"[PANEL] Error ejecutando {accion}: {exc}")
    return True


def al_hacer_clic_panel(evento, x, y, flags, parametros):
    """Gestiona tanto el movimiento (hover) como los clics en el panel lateral."""
    global salir_panel, raton_panel
    raton_panel = (x, y)

    if evento != cv2.EVENT_LBUTTONDOWN:
        return
    for _, x1, y1, x2, y2, accion in BOTONES_PANEL:
        if x1 <= x <= x2 and y1 <= y <= y2:
            if not ejecutar_accion_panel(accion, parametros):
                salir_panel = True
            break

def cerrar_camaras(camaras):
    """Detiene todas las cámaras aunque alguna falle al cerrarse."""
    print("\n[MAIN] Cerrando cámaras...")
    for camara in camaras:
        try:
            camara.cerrar()
            print(f"[MAIN] {camara.nombre}: cerrada.")
        except Exception as exc:
            print(f"[MAIN] Error cerrando {getattr(camara, 'nombre', 'cámara')}: {exc}")

    try:
        cv2.destroyAllWindows()
    except Exception:
        pass


def main():
    global CAMARAS, seleccionada, salir_panel

    preparar_carpetas()
    CAMARAS = iniciar_camaras()

    if not CAMARAS:
        print("[MAIN] No se ha podido inicializar ninguna cámara.")
        return
    
    notificaciones.iniciar_bot_comandos(CAMARAS)
    seleccionada = 0
    salir_panel = False
    cv2.namedWindow(VENTANA, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(VENTANA, ANCHO_TOTAL_BASE + ANCHO_PANEL, ALTO_TOTAL_BASE)
    def gestionar_raton(evento, x, y, flags, params):
        global raton_panel
        if x >= ANCHO_TOTAL_BASE:
            al_hacer_clic_panel(evento, x - ANCHO_TOTAL_BASE, y, flags, params)
        else:
            raton_panel = (-1, -1)
            al_hacer_clic(evento, x, y, flags, params)

    cv2.setMouseCallback(VENTANA, gestionar_raton, CAMARAS)
    # -------------------------------

    print("\n========== CONTROLES ==========")

    print("\n========== CONTROLES ==========")
    print("Panel lateral: clic en los botones")
    print("Ratón: seleccionar cámara")
    print("Flechas: mover PTZ | +/-: zoom")
    print("M: detección | R: grabación | F: captura auto")
    print("Espacio: foto | V: audio | T: micrófono")
    print("1/2/3: luz blanca / IR / auto")
    print("Q / ESC: salir")
    print("===============================\n")

    try:
        while not salir_panel:
            lienzo_camaras = dibujar_interfaz(CAMARAS, seleccionada)
            panel = dibujar_panel(seleccionada, CAMARAS)
            lienzo = np.hstack((lienzo_camaras, panel))
            cv2.imshow(VENTANA, lienzo)

            # 1. Procesamos los eventos de ventana y teclado
            tecla = cv2.waitKeyEx(30)

            # 2. Comprobamos AQUÍ (después de waitKeyEx y antes de repetir imshow)
            try:
                if cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except cv2.error:
                break

            if tecla == -1:
                continue
            tecla_ascii = tecla & 0xFF
            if tecla_ascii in (27, ord("q"), ord("Q")):
                break

            if seleccionada >= len(CAMARAS):
                continue

            camara = CAMARAS[seleccionada]
            if tecla in TODAS_LAS_FLECHAS:
                mover_ptz(camara, tecla)
            else:
                controlar_camara(camara, tecla_ascii)

    except KeyboardInterrupt:
        print("\n[MAIN] Interrupción recibida.")
    finally:
        cerrar_camaras(CAMARAS)


if __name__ == "__main__":
    main()
