import time, network
from umqtt.simple import MQTTClient

# Configuración de la red WiFi
SSID = "CONSOLA X32"
PASSWORD_WLAN = "X32.consola"

# Configuración de la conexión MQTT
SERVER = "100.26.209.37"
PORT = 1883
USER = "guest"
PASSWORD = "guest"
CLIENT_ID = "Sensor"
TOPIC = "mensajes"

# Conectar a la red WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Conectando a la red WiFi...")
    wlan.connect(SSID,PASSWORD_WLAN)
    while not wlan.isconnected():
        pass
    print("Conexión WiFi establecida. Dirección IP:", wlan.ifconfig()[0])

band = 0
while True:
    # Conectar al servidor MQTT y publicar el mensaje
    print("Conectando al servidor MQTT...")
    client = MQTTClient(CLIENT_ID, SERVER, PORT, USER, PASSWORD)
    client.connect()
    MESSAGE = str(150)
    band += 1
    if band == 10:
        band = 0
    try:
        client.publish(TOPIC, MESSAGE, retain=False, qos=0)
        print("Mensaje MQTT publicado en el tema", TOPIC)
    except OSError:
        print("Error al conectar al servidor MQTT")
    finally:
        client.disconnect()
    time.sleep(10)
