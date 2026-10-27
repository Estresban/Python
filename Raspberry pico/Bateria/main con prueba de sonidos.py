import machine
import time
from i2c_lcd import I2cLcd

# --- CONFIGURACIÓN DE RENDIMIENTO DE AUDIO ---
# --- MICROPAUSA_US = 25 para 40.000 kHz
# --- MICROPAUSA_US = 45 para 22.050 kHz
# --- MICROPAUSA_US = 22 para 44.100 kHz

MICROPAUSA_US = 22  

# --- CONFIGURACIÓN DE PERSONALIZACIÓN ---
CARACTER_SENSIBILIDAD = "*"  
CARACTER_VOLUMEN = "*"       

# --- CONFIGURACIÓN DE HARDWARE ---
s0 = machine.Pin(2, machine.Pin.OUT)
s1 = machine.Pin(3, machine.Pin.OUT)
s2 = machine.Pin(4, machine.Pin.OUT)
adc_multiplexor = machine.ADC(machine.Pin(26))

pin_seleccion = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN) 
pin_mas = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)       
pin_menos = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_DOWN)     

AUDIO_PIN = 14
pwm_audio = machine.PWM(machine.Pin(AUDIO_PIN))
pwm_audio.freq(100000) 
pwm_audio.duty_u16(0)

# --- INICIALIZACIÓN DE PANTALLA LCD I2C ---
I2C_ADDR = 0x3F  
pin_sda = machine.Pin(0, machine.Pin.ALT, pull=machine.Pin.PULL_UP)
pin_scl = machine.Pin(1, machine.Pin.ALT, pull=machine.Pin.PULL_UP)
i2c = machine.I2C(0, sda=pin_sda, scl=pin_scl, freq=100000)

lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

# --- VARIABLES DEL SISTEMA DE BATERÍA ---
NUM_PADS = 6
# NUM_PADS = 7
NOMBRES_PADS = ["BOMBO", "CAJA", "TO1", "TO2", "HIHAT", "PLATO"]
# NOMBRES_PADS = ["BOMBO", "CAJA", "TO1", "TO2", "HIHAT", "PLATO", "RESERVA"]

niveles_sensibilidad = [5] * NUM_PADS  
sensibilidades = [0] * NUM_PADS  
volumenes_pads = [3] * NUM_PADS      
referencias_estaticas = [0] * NUM_PADS

KITS = ["Rock", "Heavy", "Blues", "Pop", "Folk", "Tecno"]
kit_actual_idx = 0

tiempo_ultimo_golpe = [0] * NUM_PADS
cooldown_ms = 45  

MODO_MENU = 0  # 0: Play, 1: Cambiar Kit, 2: Volumen General, 3: Sensibilidad, 4: Test Hardware
pad_seleccionado_idx = 0 
volumen_general = 7 

tiempo_ultimo_menu = 0
COOLDOWN_BOTONES = 120 

fuerza_vumetro_actual = 0
tiempo_ultimo_decay = 0

TABLA_PASOS_MULTIPLEXOR = [
    (0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1)
]

# TABLA_PASOS_MULTIPLEXOR = [
#   (0, 0, 0), # Canal 0 (C0)
#    (1, 0, 0), # Canal 1 (C1)
#    (0, 1, 0), # Canal 2 (C2)
#    (1, 1, 0), # Canal 3 (C3)
#    (0, 0, 1), # Canal 4 (C4)
#    (1, 0, 1), # Canal 5 (C5)
#    (0, 1, 1)  # 👈 Canal 6 (C6) - NUEVO PAD
#    (1, 1, 1)  # 👈 Canal 7 (C7) - NUEVO PAD
#]

ARCHIVOS_INSTRUMENTOS = [
    "Bombo.wav", "Caja.wav", "Tom1.wav", "Tom2.wav", "Hihat.wav", "Plato.wav"
]

# ARCHIVOS_INSTRUMENTOS = [
#     "Bombo.wav", "Caja.wav", "Tom1.wav", "Tom2.wav", "Hihat.wav", "Plato.wav", "Cencerro.wav"
# ]

CUSTOM_CHARS = [
    [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10], 
    [0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18], 
    [0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C], 
    [0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E], 
    [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F]  
]

for i, char_data in enumerate(CUSTOM_CHARS):
    lcd.custom_char(i, bytearray(char_data))

# --- FUNCIONES DE ALMACENAMIENTO ---

def guardar_configuracion():
    try:
        with open("config.txt", "w") as f:
            f.write("{}\n".format(kit_actual_idx))
            f.write("{}\n".format(volumen_general))
            f.write(",".join([str(n) for n in niveles_sensibilidad]) + "\n")
    except:
        pass

def cargar_configuracion():
    global kit_actual_idx, volumen_general, niveles_sensibilidad
    try:
        with open("config.txt", "r") as f:
            kit_actual_idx = int(f.readline().strip())
            volumen_general = int(f.readline().strip())
            sens_data = f.readline().strip().split(",")
            if len(sens_data) == NUM_PADS:
                niveles_sensibilidad = [int(x) for x in sens_data]
    except:
        pass

def auto_calibrar_y_guardar_referencia():
    global referencias_estaticas
    for i in range(NUM_PADS):
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
    
    # Calculamos cuántos bloques de la pantalla corresponden a cada pad (16 columnas / 6 pads)
    columnas_por_pad = 16 // NUM_PADS 
    
    for i in range(NUM_PADS):
        # 1. Dibujamos visualmente la barra en la pantalla LCD
        for c in range(columnas_por_pad):
            columna_actual = (i * columnas_por_pad) + c
            if columna_actual < 16:
                lcd.move_to(columna_actual, 1)
                lcd.putstr(chr(4))
                
        # 2. Construimos la ruta del archivo correspondiente al kit por defecto (rock)
        ruta_sound = "{}/{}".format(KITS[kit_actual_idx].lower(), ARCHIVOS_INSTRUMENTOS[i])
        
        # 3. Reproducimos el sonido actual (el número 3 es el volumen asignado por defecto al pad)
        reproducir_audio_wav(ruta_sound, 5)
        
        # Pequeña pausa de 150 milisegundos entre un instrumento y otro para que no se encabalguen
        time.sleep_ms(150) 
        
    # Si quedan espacios vacíos al final de la barra de la LCD por el redondeo, los llenamos
    for col_restante in range((NUM_PADS * columnas_por_pad), 16):
        lcd.move_to(col_restante, 1)
        lcd.putstr(chr(4))
        
    time.sleep_ms(500)
    lcd.clear()

def seleccionar_canal_multiplexor(canal):
    estados = TABLA_PASOS_MULTIPLEXOR[canal]
    s0.value(estados[0])
    s1.value(estados[1])
    s2.value(estados[2])

def calcular_umbral_adc(pad_idx):
    nivel = niveles_sensibilidad[pad_idx]
    distancia_threshold = 35000 - (nivel * 3000)
    return referencias_estaticas[pad_idx] + distancia_threshold

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
    global MODO_MENU
    
    if MODO_MENU == 0:
        lcd.move_to(0, 0)
        lcd.putstr(("Lista: " + KITS[kit_actual_idx] + "               ")[:16]) 
        lcd.move_to(0, 1)
        texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
        lcd.putstr(texto_barra)
        
    elif MODO_MENU == 1:
        lcd.move_to(0, 0)
        lcd.putstr("1-MENU: Sel. Kit ") 
        lcd.move_to(0, 1)
        lcd.putstr(("Kit: " + KITS[kit_actual_idx] + "               ")[:16])
        
    elif MODO_MENU == 2:
        lcd.move_to(0, 0)
        lcd.putstr("2-MENU: Volumen  ") 
        barras_vol = "".join([CARACTER_VOLUMEN for _ in range(volumen_general)])
        texto_linea2 = "Nivel:" + (barras_vol if volumen_general > 0 else "MUTEADA")
        lcd.move_to(0, 1)
        lcd.putstr((texto_linea2 + "                ")[:16])
        
    elif MODO_MENU == 3:
        lcd.move_to(0, 0)
        lcd.putstr(("3-SENS: " + NOMBRES_PADS[pad_seleccionado_idx] + "               ")[:16]) 
        nivel_actual = niveles_sensibilidad[pad_seleccionado_idx]
        barras_sens = "".join([CARACTER_SENSIBILIDAD for _ in range(nivel_actual)])
        lcd.move_to(0, 1)
        lcd.putstr(("Nivel:" + barras_sens + "                ")[:16])
        
    elif MODO_MENU == 4:
        lcd.move_to(0, 0)
        lcd.putstr("4-TEST HARDWARE") 

def mostrar_golpe_vumetro(pad, lectura):
    if MODO_MENU != 0:
        return
    base = sensibilidades[pad]
    rango = 65535 - base
    fuerza = int(((lectura - base) / rango) * 80)
    fuerza = max(0, min(80, fuerza))
    texto_barra = generar_vumetro_16_caracteres(fuerza)
    lcd.move_to(0, 1)
    lcd.putstr(texto_barra)

def reproducir_audio_wav(ruta_archivo, factor_volumen):
    try:
        with open(ruta_archivo, "rb") as f:
            f.seek(44) 
            escala = (factor_volumen / 4.0) * (volumen_general / 10.0)
            while True:
                if pin_seleccion.value() == 1 or pin_mas.value() == 1 or pin_menos.value() == 1:
                    break
                datos = f.read(512)
                if not datos:
                    break
                for muestra in datos:
                    valor_pwm = int(muestra * 256 * escala)
                    pwm_audio.duty_u16(valor_pwm)
                    time.sleep_us(MICROPAUSA_US)
            pwm_audio.duty_u16(0)
    except:
        pass

# --- CONFIGURACIÓN DE ARRANQUE ---
cargar_configuracion()
auto_calibrar_y_guardar_referencia() 

for p in range(NUM_PADS):
    sensibilidades[p] = calcular_umbral_adc(p)

animacion_inicio()    
actualizar_pantalla()

# --- BUCLE PRINCIPAL ---
while True:
    tiempo_actual = time.ticks_ms()
    
    # 1. BOTÓN MENÚ
    if pin_seleccion.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > COOLDOWN_BOTONES:
            MODO_MENU = (MODO_MENU + 1) % 5
            actualizar_pantalla()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 2. BOTÓN MÁS
    if pin_mas.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > COOLDOWN_BOTONES:
            if MODO_MENU == 1:
                kit_actual_idx = (kit_actual_idx + 1) % len(KITS)
                actualizar_pantalla()
                guardar_configuracion()
            elif MODO_MENU == 2:
                if volumen_general < 10:
                    volumen_general += 1
                    actualizar_pantalla()
                    guardar_configuracion()
            elif MODO_MENU == 3:
                if niveles_sensibilidad[pad_seleccionado_idx] < 9:
                    niveles_sensibilidad[pad_seleccionado_idx] += 1
                    sensibilidades[pad_seleccionado_idx] = calcular_umbral_adc(pad_seleccionado_idx)
                    actualizar_pantalla()
                    guardar_configuracion()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 3. BOTÓN MENOS
    if pin_menos.value() == 1:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_menu) > COOLDOWN_BOTONES:
            if MODO_MENU == 1:
                kit_actual_idx = (kit_actual_idx - 1) % len(KITS)
                actualizar_pantalla()
                guardar_configuracion()
            elif MODO_MENU == 2:
                if volumen_general > 0:
                    volumen_general -= 1
                    actualizar_pantalla()
                    guardar_configuracion()
            elif MODO_MENU == 3:
                if niveles_sensibilidad[pad_seleccionado_idx] > 1:
                    niveles_sensibilidad[pad_seleccionado_idx] -= 1
                    sensibilidades[pad_seleccionado_idx] = calcular_umbral_adc(pad_seleccionado_idx)
                    actualizar_pantalla()
                    guardar_configuracion()
            tiempo_ultimo_menu = tiempo_actual
            continue

    # 4. CAÍDA SUAVE DEL VÚMETRO ASÍNCRONO
    if MODO_MENU == 0 and fuerza_vumetro_actual > 0:
        if time.ticks_diff(tiempo_actual, tiempo_ultimo_decay) > 15:
            fuerza_vumetro_actual = max(0, fuerza_vumetro_actual - 3)
            texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
            lcd.move_to(0, 1)
            lcd.putstr(texto_barra)
            tiempo_ultimo_decay = tiempo_actual

    # 5. ESCANEO DEL MULTIPLEXOR
    pad_mas_fuerte_idx = -1
    lectura_maxima = 0
    
    for i in range(NUM_PADS):
        seleccionar_canal_multiplexor(i)
        lectura = adc_multiplexor.read_u16()
        
        # Formato de la fila 2 para el menú 4 (Test de Hardware)
        if MODO_MENU == 4 and i == pad_seleccionado_idx:
            lcd.move_to(0, 1)
            lcd.putstr("{}:B{} V{}   ".format(NOMBRES_PADS[i][:3], referencias_estaticas[i], lectura)[:16])
            
        if lectura > sensibilidades[i]:
            if time.ticks_diff(tiempo_actual, tiempo_ultimo_golpe[i]) > cooldown_ms:
                if lectura > lectura_maxima:
                    lectura_maxima = lectura
                    pad_mas_fuerte_idx = i

    if pad_mas_fuerte_idx != -1:
        i = pad_mas_fuerte_idx
        tiempo_ultimo_golpe[i] = tiempo_actual
        
        if MODO_MENU == 3 or MODO_MENU == 4:
            pad_seleccionado_idx = i
            actualizar_pantalla()
        
        if MODO_MENU == 0:
            base = sensibilidades[i]
            rango = 65535 - base
            fuerza_vumetro_actual = int(((lectura_maxima - base) / rango) * 80)
            fuerza_vumetro_actual = max(0, min(80, fuerza_vumetro_actual))
            
            texto_barra = generar_vumetro_16_caracteres(fuerza_vumetro_actual)
            lcd.move_to(0, 1)
            lcd.putstr(texto_barra)
            tiempo_ultimo_decay = tiempo_actual
            
            if pin_mas.value() == 1:
                volumenes_pads[i] = (volumenes_pads[i] + 1) % 5
        
        ruta_final = "{}/{}".format(KITS[kit_actual_idx].lower(), ARCHIVOS_INSTRUMENTOS[i])
        reproducir_audio_wav(ruta_final, volumenes_pads[i])

