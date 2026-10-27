from machine import UART, Pin
import time

# Configuración exacta descubierta para tu placa clon W-2023
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=2000)

print("1. Despertando el chip WiFi (ESP8285)...")
uart.write(b"AT\r\n")
time.sleep(0.5)
respuesta = uart.read()
if respuesta and b"OK" in respuesta:
    print("-> Chip conectado y listo.\n")
else:
    print("-> No se pudo conectar con el chip. Reinicia el USB de la placa.\n")

print("2. Configurando el chip en Modo Cliente (Estación)...")
uart.write(b"AT+CWMODE=1\r\n")
time.sleep(0.5)
# Limpiar el búfer de texto recibido
uart.read()

print("3. Escaneando redes WiFi de la zona...")
print("   (Espera unos 5 segundos, por favor...)\n")
uart.write(b"AT+CWLAP\r\n")

# Damos 5 segundos para que busque todas las ondas físicas de radio
time.sleep(5)

resultado_escaneo = uart.read()
if resultado_escaneo:
    print("--- ¡REDES DETECTADAS! ---")
    # Versión corregida: decodificamos el texto de forma simple y directa
    texto_redes = resultado_escaneo.decode()
    print(texto_redes)
else:
    print("No se recibieron datos del escaneo. Inténtalo de nuevo.")
