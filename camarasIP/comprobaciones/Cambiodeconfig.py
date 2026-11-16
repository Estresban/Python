from dvrip import DVRIPCam

# Conecta al puerto nativo 34567 de la cámara del garaje
cam = DVRIPCam("192.168.1.22", user="pbny", password="ur2uh8")

if cam.login():
    print("¡Conectado al puerto 34567 de la cámara del garaje!")
    
    # Activa el servicio ONVIF en el puerto 8899
    cam.set_info("NetWork.Onvif", {"Enable": True, "Port": 8899})
    
    # Activa el servicio RTSP en el puerto 554
    cam.set_info("NetWork.RTSP", {"Enable": True, "Port": 554})
    
    print("Servicios ONVIF y RTSP activados. Reiniciando cámara...")
    cam.reboot()
    cam.close()
else:
    print("Error de inicio de sesión en el puerto 34567. Verifica la contraseña.")
