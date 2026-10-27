import machine
import time
import _thread
from i2c_lcd import I2cLcd

# --- CONFIGURACIÓN DE RENDIMIENTO DE AUDIO ---
micropausa_us = 22  # Ajustado para audio para 44.100 kHz
# --- CONFIGURACIÓN DE RENDIMIENTO DE AUDIO ---
# --- micropausa_us = 25 para 40.000 kHz
# --- micropausa_us = 45 para 22.050 kHz
# --- micropausa_us = 22 para 44.100 kHz

# --- CONFIGURACIÓN DE PERSONALIZACIÓN ---

caracter_especial = "*"    

# --- CONFIGURACIÓN DE HARDWARE ---
s0 = machine.Pin(2, machine.Pin.OUT)
s1 = machine.Pin(3, machine.Pin.OUT)
s2 = machine.Pin(4, machine.Pin.OUT)
adc_multiplexor = machine.ADC(machine.Pin(26))

pin_seleccion = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)
pin_mas = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)       
pin_menos = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_DOWN)    

pin_audio = 14
pwm_audio = machine.PWM(machine.Pin(pin_audio))
pwm_audio.freq(100000)
pwm_audio.duty_u16(32768) # Inicializa en el punto medio exacto para eliminar el chasquido inicial

# --- INICIALIZACIÓN DE PANTALLA LCD I2C ---
Direccion_I2C = 0x3F 
pin_sda = machine.Pin(0, machine.Pin.ALT, pull=machine.Pin.PULL_UP)
pin_scl = machine.Pin(1, machine.Pin.ALT, pull=machine.Pin.PULL_UP)
i2c = machine.I2C(0, sda=pin_sda, scl=pin_scl, freq=100000)
lcd = I2cLcd(i2c, Direccion_I2C, 2, 16)

# --- VARIABLES DEL SISTEMA DE BATERÍA ---
pads = 6
nombre_pads = ["BOMBO", "CAJA", "TO1", "TO2", "HIHAT", "PLATO"]
# pads = 7
# nombre_pads = ["BOMBO", "CAJA", "TO1", "TO2", "HIHAT", "PLATO", "RESERVA"]

niveles_sensibilidad = [5] * pads 
sensibilidades = [0] * pads 
volumenes_pads = [3] * pads     
referencias_estaticas = [0] * pads

kits = ["Rock", "Heavy", "Blues", "Pop", "Folk", "Tecno"]
kit_actual_indice = 0

tiempo_ultimo_golpe = [0] * pads
recuperacion_us = 45 

modo_menu = 0 
pad_seleccionado_indice = 0
volumen_general = 7

tiempo_ultimo_menu = 0
recuperacion_botones = 120

fuerza_vumetro_actual = 0
tiempo_ultimo_declive = 0

binario_multiplexor = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1)]
archivos_instrumentos = ["Bombo.wav", "Caja.wav", "Tom1.wav", "Tom2.wav", "Hihat.wav", "Plato.wav"]
#binario_multiplexor = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1)]
#archivos_instrumentos = ["Bombo.wav", "Caja.wav", "Tom1.wav", "Tom2.wav", "Hihat.wav", "Plato.wav", "Reserva.wav"]


Bloque = [
    [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10], 
    [0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18], 
    [0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C], 
    [0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E], 
    [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F]  
]

for i, char_data in enumerate(Bloque):
    lcd.custom_char(i, bytearray(char_data))

# --- VARIABLES GLOBALES DE INTERCONEXIÓN ENTRE CORES ---
ruta_solicitada = ""
volumen_solicitado = 0
bloqueo_audio = _thread.allocate_lock()

# --- FUNCIONES DE ALMACENAMIENTO ---
def guardar_configuracion():
    try:
        with open("config.txt", "w") as f:
            f.write("{}\n".format(kit_actual_indice))
            f.write("{}\n".format(volumen_general))
            f.write(",".join([str(n) for n in niveles_sensibilidad]) + "\n")
    except:
        pass

def cargar_configuracion():
    global kit_actual_indice, volumen_general, niveles_sensibilidad
    try:
        with open("config.txt", "r") as f:
            kit_actual_indice = int(f.readline().strip())
            volumen_general = int(f.readline().strip())
            sens_datos = f.readline().strip().split(",")
            if len(sens_datos) == pads:
                niveles_sensibilidad = [int(x) for x in sens_datos]
    except:
        pass

def auto_calibrar_y_guardar_referencia():
    global referencias_estaticas
    for i in range(pads):
        seleccionar_canal_multiplexor(i)
        time.sleep_ms(5)
        suma_lecturas = 0
        for _ in range(10):
            suma_lecturas += adc_multiplexor.read_u16()
            time.sleep_ms(2)
        referencias_estaticas[i] = suma_lecturas // 10
        
    try:
        with open("test.txt", "w") as f:
            f.write(",".join([str(r) for r in referencias_estaticas]) + "\n")
    except:
        pass

# --- FUNCIONES DE INTERFAZ ---
def animacion_inicio():
    lcd.clear()
    lcd.move_to(2, 0)
    lcd.putstr("Stivi Bateria") 
    for i in range(16):
        lcd.move_to(i, 1)
        lcd.putstr(chr(4))
        time.sleep_ms(100) 
    time.sleep_ms(500)
    lcd.clear()

def seleccionar_canal_multiplexor(canal):
    estados = binario_multiplexor[canal]
    s0.value(estados[0])
    s1.value(estados[1])
    s2.value(estados[2])

def calcular_umbral_adc(pad_indice):
    nivel = niveles_sensibilidad[pad_indice]
    distancia_threshold = 35000 - (nivel * 3000)
    return referencias_estaticas[pad_indice] + distancia_threshold

def generar_vumetro_16_caracteres(fuerza_relativa):
    bloques_llenos = fuerza_relativa // 5
    residuo = fuerza_relativa % 5
    resultado = ""
    for _ in range(bloques_llenos):
        resultado += chr(4) 
    if residuo > 0 and len(resultado) < 16:
        resultado += chr(residuo - 1) 
    while len(resultado) < 16:
        resultado += "." 
    return resultado

def actualizar_pantalla():
    global modo_menu
    if modo_menu == 0:
        lcd.move_to(0, 0)
        lcd.putstr(("Lista: " + kits[kit_actual_indice] + "               ")[:16]) 
        lcd.move_to(0, 1)
        texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
        lcd.putstr(texto_barra)
    elif modo_menu == 1:
        lcd.move_to(0, 0)
        lcd.putstr("1-MENU: Sel. Kit ") 
        lcd.move_to(0, 1)
        lcd.putstr(("Kit: " + kits[kit_actual_indice] + "               ")[:16])
    elif modo_menu == 2:
        lcd.move_to(0, 0)
        lcd.putstr("2-MENU: Volumen  ") 
        barras_vol = "".join([caracter_especial for _ in range(volumen_general)])
        texto_linea2 = "Nivel:" + (barras_vol if volumen_general > 0 else "MUTEADA")
        lcd.move_to(0, 1)
        lcd.putstr((texto_linea2 + "                ")[:16])
    elif modo_menu == 3:
        lcd.move_to(0, 0)
        lcd.putstr(("3-SENS: " + nombre_pads[pad_seleccionado_indice] + "               ")[:16]) 
        nivel_actual = niveles_sensibilidad[pad_seleccionado_indice]
        barras_sens = "".join([caracter_especial for _ in range(nivel_actual)])
        lcd.move_to(0, 1)
        lcd.putstr(("Nivel:" + barras_sens + "                ")[:16])
    elif modo_menu == 4:
        lcd.move_to(0, 0)
        lcd.putstr("4-TEST HARDWARE") 

# --- HILO DE AUDIO EXCLUSIVO (CORE 1) ---
def ejecucion_core_1():
    # 1. Indicamos las variables globales
    global ruta_solicitada, volumen_solicitado, volumen_general
    
    # 2. TRUCO DE SEGURIDAD: Si el Core 0 aún no las ha creado por lentitud en el arranque, las inicializamos aquí
    if 'ruta_solicitada' not in globals():
        ruta_solicitada = ""
    if 'volumen_solicitado' not in globals():
        volumen_solicitado = 0
    if 'volumen_general' not in globals():
        volumen_general = 7
        
    print("Core 1: Sistema de audio activo.")
  
    while True:
        if ruta_solicitada != "":
            # Extraemos de forma segura la petición del Core 0
            bloqueo_audio.acquire()
            archivo = ruta_solicitada
            factor_volumen = volumen_solicitado
            ruta_solicitada = "" # Limpiamos la orden anterior
            bloqueo_audio.release()
            
            try:
                with open(archivo, "rb") as f:
                    f.seek(44) # Saltar cabecera WAV
                    #escala = (factor_volumen / 4.0) * (volumen_general / 10.0)
                    escala = float((factor_volumen / 4.0) * (volumen_general / 10.0))
                    while True:
                        # Si se presiona algún botón en el Core 0, rompemos la reproducción
                        if pin_seleccion.value() == 1 or pin_mas.value() == 1 or pin_menos.value() == 1:
                            break
                        
                        datos = f.read(256) # Buffer de muestras
                        if not datos:
                            break
                        
                        for muestra in datos:
                            t_inicio = time.ticks_us()
                            #valor_pwm = int(muestra * 256 * escala)
                            valor_pwm = int((muestra - 128) * 256 * escala) + 32768
                            pwm_audio.duty_u16(valor_pwm)
                            
                            # Temporizador estricto por hardware
                            while time.ticks_diff(time.ticks_us(), t_inicio) < micropausa_us:
                                pass
                                
            except Exception as e:
                print("Error de lectura:", e)
            finally:
                # Al terminar la muestra, regresamos al punto medio de 1.65V (Evita el "click" final)
                pwm_audio.duty_u16(32768) 
                
        time.sleep_ms(1) # Liberación del núcleo en reposo

# --- CONFIGURACIÓN DE ARRANQUE ---
cargar_configuracion()
auto_calibrar_y_guardar_referencia()  

for p in range(pads):
    sensibilidades[p] = calcular_umbral_adc(p)

animacion_inicio()    
actualizar_pantalla()

# CAMBIO: Le damos 50ms al Core 0 para que asiente las variables en memoria antes de despertar al Core 1
time.sleep_ms(50)

# Lanzamos el Hilo de Audio al Core 1 antes de arrancar el bucle del Core 0
_thread.start_new_thread(ejecucion_core_1, ())

# --- BUCLE PRINCIPAL (CORE 0) ---
while True:
    tiempo_actual = time.ticks_ms()
    
    # 1. BOTÓN MENÚ
    if pin_seleccion.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > recuperacion_botones:
            modo_menu = (modo_menu + 1) % 5
            actualizar_pantalla()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 2. BOTÓN MÁS
    if pin_mas.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > recuperacion_botones:
            if modo_menu == 1:
                kit_actual_indice = (kit_actual_indice + 1) % len(kits)
                actualizar_pantalla()
                guardar_configuracion()
            elif modo_menu == 2:
                if volumen_general < 10:
                    volumen_general += 1
                    actualizar_pantalla()
                    guardar_configuracion()
            elif modo_menu == 3:
                if niveles_sensibilidad[pad_seleccionado_indice] < 9:
                    niveles_sensibilidad[pad_seleccionado_indice] += 1
                    sensibilidades[pad_seleccionado_indice] = calcular_umbral_adc(pad_seleccionado_indice)
                    actualizar_pantalla()
                    guardar_configuracion()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 3. BOTÓN MENOS
    if pin_menos.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > recuperacion_botones:
            if modo_menu == 1:
                kit_actual_indice = (kit_actual_indice - 1) % len(kits)
                actualizar_pantalla()
                guardar_configuracion()
            elif modo_menu == 2:
                if volumen_general > 0:
                    volumen_general -= 1
                    actualizar_pantalla()
                    guardar_configuracion()
            elif modo_menu == 3:
                if niveles_sensibilidad[pad_seleccionado_indice] > 1:
                    niveles_sensibilidad[pad_seleccionado_indice] -= 1
                    sensibilidades[pad_seleccionado_indice] = calcular_umbral_adc(pad_seleccionado_indice)
                    actualizar_pantalla()
                    guardar_configuracion()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 4. CAÍDA SUAVE DEL VÚMETRO
    if modo_menu == 0 and fuerza_vumetro_actual > 0:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_declive) > 15:
            fuerza_vumetro_actual = max(0, fuerza_vumetro_actual - 3)
            texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
            lcd.move_to(0, 1)
            lcd.putstr(texto_barra)
            tiempo_ultimo_declive = tiempo_actual

    # 5. ESCANEO DEL MULTIPLEXOR
    pad_mas_fuerte_indice = -1
    lectura_maxima = 0
    
    for i in range(pads):
        seleccionar_canal_multiplexor(i)
        lectura = adc_multiplexor.read_u16()
        
        if modo_menu == 4 and i == pad_seleccionado_indice:
            lcd.move_to(0, 1)
            lcd.putstr("{}:B{} V{}   ".format(nombre_pads[i][:3], referencias_estaticas[i], lectura)[:16])
            
        if lectura > sensibilidades[i]:
            if time.ticks_diff(tiempo_actual, tiempo_ultimo_golpe[i]) > recuperacion_us:
                if lectura > lectura_maxima:
                    lectura_maxima = lectura
                    pad_mas_fuerte_indice = i

    if pad_mas_fuerte_indice != -1:
        i = pad_mas_fuerte_indice
        tiempo_ultimo_golpe[i] = tiempo_actual
        
        if modo_menu == 3 or modo_menu == 4:
            pad_seleccionado_indice = i
            actualizar_pantalla()
        
        if modo_menu == 0:
            base = sensibilidades[i]
            rango = 65535 - base
            fuerza_vumetro_actual = int(((lectura_maxima - base) / rango) * 80)
            fuerza_vumetro_actual = max(0, min(80, fuerza_vumetro_actual))
            
            texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
            lcd.move_to(0, 1)
            lcd.putstr(texto_barra)
            tiempo_ultimo_declive = tiempo_actual
            
            if pin_mas.value() == 1:
                volumenes_pads[i] = (volumenes_pads[i] + 1) % 5
        
        # Enviar petición al Core 1 usando el Lock de hilos de forma segura
        if not bloqueo_audio.locked() and ruta_solicitada == "":
            bloqueo_audio.acquire()
            ruta_solicitada = "{}/{}".format(kits[kit_actual_indice].lower(), archivos_instrumentos[i])
            volumen_solicitado = volumenes_pads[i]
            bloqueo_audio.release()
            
    time.sleep_us(50)  # Micro-pausa para estabilizar los procesos generales

