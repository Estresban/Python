import network
import socket
import machine
import time
import ntptime
import _thread

# --- CONFIGURACIÓN WI-FI ---
WIFI_SSID = "VICARIO"
WIFI_PASS = "AlaProximaTeFundo!1"

# --- CONFIGURACIÓN DE PINES (NodeMCU V3) ---
# Usamos pines seguros que no interfieran en el arranque del ESP8266
PIN_RELE_SUBIR = 5   # Pin D1 en NodeMCU
PIN_RELE_BAJAR = 4   # Pin D2 en NodeMCU
PIN_PULS_SUBIR = 14  # Pin D5 en NodeMCU (Con resistencia PULL_UP interna)
PIN_PULS_BAJAR = 12  # Pin D6 en NodeMCU (Con resistencia PULL_UP interna)

# Configurar Salidas (Relés)
rele_subir = machine.Pin(PIN_RELE_SUBIR, machine.Pin.OUT, value=0)
rele_bajar = machine.Pin(PIN_RELE_BAJAR, machine.Pin.OUT, value=0)

# Configurar Entradas (Pulsadores físicos al presionar mandan 0/GND)
pulsador_subir = machine.Pin(PIN_PULS_SUBIR, machine.Pin.IN, machine.Pin.PULL_UP)
pulsador_bajar = machine.Pin(PIN_PULS_BAJAR, machine.Pin.IN, machine.Pin.PULL_UP)

# --- VARIABLES DE ESTADO Y PROGRAMACIÓN ---
estado_persiana = "Detenida"
# Horarios por defecto (Formato 24h: Hora, Minuto)
hora_subida = [8, 0]
hora_bajada = [20, 30]

# --- CONEXIÓN A INTERNET Y HORA ---
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    print("Conectando a la red...", end="")
    intentos = 0
    while not wlan.isconnected() and intentos < 20:
        time.sleep(1)
        intentos += 1
    
    if wlan.isconnected():
        print("\n¡Conectado! Dirección IP:", wlan.ifconfig()[0])
        try:
            ntptime.settime() # Sincroniza la hora interna con internet (UTC)
            print("Hora UTC sincronizada.")
        except:
            print("Error al sincronizar la hora con NTP.")
    else:
        print("\nNo se pudo conectar al Wi-Fi.")

# --- CONTROL SEGURO DE LA PERSIANA ---
def mover_persiana(accion):
    global estado_persiana
    if accion == "SUBIR":
        rele_bajar.value(0) # Enclavamiento de seguridad: apaga el motor contrario
        time.sleep(0.2)
        rele_subir.value(1)
        estado_persiana = "Subiendo"
    elif accion == "BAJAR":
        rele_subir.value(0) # Enclavamiento de seguridad
        time.sleep(0.2)
        rele_bajar.value(1)
        estado_persiana = "Bajando"
    elif accion == "PARAR":
        rele_subir.value(0)
        rele_bajar.value(0)
        estado_persiana = "Detenida"

# --- HILO DE MONITOREO DE PULSADORES Y HORARIOS ---
def bucle_fondo():
    global hora_subida, hora_bajada
    ultimo_minuto_comprobado = -1
    
    while True:
        # 1. Monitorear pulsadores físicos (Lógica inversa debido al PULL_UP)
        if pulsador_subir.value() == 0:
            mover_persiana("SUBIR" if estado_persiana != "Subiendo" else "PARAR")
            time.sleep(0.5) # Anti-rebote elemental
            
        if pulsador_bajar.value() == 0:
            mover_persiana("BAJAR" if estado_persiana != "Bajando" else "PARAR")
            time.sleep(0.5)

        # 2. Control Horario Automático (Ajustar la hora UTC local sumando la zona horaria)
        # Ejemplo para España en invierno (UTC+1). En verano cambiar a +2.
        zona_horaria = 1 
        tiempo_local = time.time() + (zona_horaria * 3600)
        fecha_hora = time.localtime(tiempo_local)
        
        hora_actual = fecha_hora[3]
        minuto_actual = fecha_hora[4]
        
        if minuto_actual != ultimo_minuto_comprobado:
            # Comprobar hora de subir
            if hora_actual == hora_subida[0] and minuto_actual == hora_subida[1]:
                mover_persiana("SUBIR")
                time.sleep(15) # Tiempo estimado en subir por completo antes de apagar relé
                mover_persiana("PARAR")
            
            # Comprobar hora de bajar
            if hora_actual == hora_bajada[0] and minuto_actual == hora_bajada[1]:
                mover_persiana("BAJAR")
                time.sleep(15) # Tiempo estimado en bajar
                mover_persiana("PARAR")
                
            ultimo_minuto_comprobado = minuto_actual
            
        time.sleep(0.1)

# --- INTERFAZ WEB DEL SERVIDOR ---
def web_page():
    # Obtener hora actual para mostrar en el panel web
    zona_horaria = 1
    ahora = time.localtime(time.time() + (zona_horaria * 3600))
    hora_str = "{:02d}:{:02d}:{:02d}".format(ahora[3], ahora[4], ahora[5])

    html = """<html>
    <head>
        <title>Control de Persiana Domotica</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" charset="utf-8">
        <style>
            body { font-family: Arial; text-align: center; margin: 20px; background-color: #f4f4f9; }
            .btn { display: inline-block; padding: 15px 25px; font-size: 18px; margin: 10px; cursor: pointer; color: white; border: none; border-radius: 5px; text-decoration: none; }
            .btn-subir { background-color: #4CAF50; }
            .btn-bajar { background-color: #008CBA; }
            .btn-parar { background-color: #f44336; }
            .btn-guardar { background-color: #555555; padding: 8px 15px; font-size: 14px; }
            .estado { font-size: 20px; font-weight: bold; color: #333; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h2>🏠 Servidor Domótico - Persiana</h2>
        <div class="estado">Estado actual: """ + estado_persiana + """</div>
        <div class="estado">Hora actual del sistema: """ + hora_str + """</div>
        
        <div>
            <a href="/?action=subir" class="btn btn-subir">🔼 Subir</a>
            <a href="/?action=parar" class="btn btn-parar">⏹️ Parar</a>
            <a href="/?action=bajar" class="btn btn-bajar">🔽 Bajar</a>
        </div>
        
        <br><hr><br>
        
        <h3>⚙️ Programación Horaria</h3>
        <form action="/" method="get">
            <label>Hora de Subida (HH:MM): </label>
            <input type="number" name="h_sub" min="0" max="23" value=""""+str(hora_subida[0])+"""" style="width: 50px;"> :
            <input type="number" name="m_sub" min="0" max="59" value=""""+str(hora_subida[1])+"""" style="width: 50px;"><br><br>
            
            <label>Hora de Bajada (HH:MM): </label>
            <input type="number" name="h_baj" min="0" max="23" value=""""+str(hora_bajada[0])+"""" style="width: 50px;"> :
            <input type="number" name="m_baj" min="0" max="59" value=""""+str(hora_bajada[1])+"""" style="width: 50px;"><br><br>
            
            <button type="submit" name="action" value="set_time" class="btn btn-guardar">Guardar Horario</button>
        </form>
    </body>
    </html>"""
    return html

# --- SERVIDOR WEB PRINCIPAL ---
def iniciar_servidor():
    global hora_subida, hora_bajada
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    print("Servidor HTTP listo en el puerto 80")
    
    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode('utf-8')
            
            # Analizar peticiones GET
            if "GET /?action=subir" in request:
                mover_persiana("SUBIR")
            elif "GET /?action=bajar" in request:
                mover_persiana("BAJAR")
            elif "GET /?action=parar" in request:
                mover_persiana("PARAR")
            elif "GET /?action=set_time" in request:
                # Extraer parámetros de los campos del formulario
                try:
                    params = request.split(' ')[1].split('?')[1].split('&')
                    p_dict = {}
                    for p in params:
                        k, v = p.split('=')
                        p_dict[k] = int(v)
                    
                    hora_subida = [p_dict['h_sub'], p_dict['m_sub']]
                    hora_bajada = [p_dict['h_baj'], p_dict['m_baj']]
                    print("Nuevo horario guardado -> Subir:", hora_subida, "Bajar:", hora_bajada)
                except Exception as e:
                    print("Error al procesar el formulario horaria:", e)

            # Responder al cliente web
            response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except Exception as e:
            print("Error en el servidor web:", e)

# --- EJECUCIÓN DEL PROGRAMA ---
conectar_wifi()

# Arrancar el monitoreo de botones y reloj en un hilo de fondo dinámico
_thread.start_new_thread(bucle_fondo, ())

# Arrancar el servidor web en el bucle principal
iniciar_servidor()
