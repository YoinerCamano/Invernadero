import urequests as requests
import json, network, time

# Configuración de la red WiFi

SSID = "CONSOLA X32"
PASSWORD_WLAN = "X32.consola"

# Configuración BOT TELEGRAM

bot_token = "5839981812:AAH7AUgJNLoeo1E2LsZqb2ay8uGe4ecwE_I"
chat_id = "1214775886"
message = "Hello from ESP32!"

# Conectar a la red WiFi

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Conectando a la red WiFi...")
    wlan.connect(SSID,PASSWORD_WLAN)
    while not wlan.isconnected():
        pass
    print("Conexión WiFi establecida. Dirección IP:", wlan.ifconfig()[0])

def bot_telegram(message):
    url = "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    headers = {
        "Content-Type": "application/json"
        }
    data_j = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=json.dumps(data_j), headers=headers)
    return response

while True:
    response = bot_telegram("¡ALERTA HUMEDAD RELATIVA BAJA, POR DEBAJO DE " + str(35) + "Grados Celcius")
    print(response.text)
    time.sleep(10)

