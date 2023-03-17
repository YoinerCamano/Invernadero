from machine import SoftI2C, Pin
from umqtt.simple import MQTTClient
import time, network

# Configuración de la red WiFi
SSID = "CONSOLA X32"
PASSWORD_WLAN = "X32.consola"

# Configuración de la conexión MQTT
SERVER = "192.168.0.103"
PORT = 1883
USER = "guest"
PASSWORD = "guest"
CLIENT_ID = "Sensor_Esp32"
TOPIC = b'Cola_Temperatura'

# Definir las constantes para la dirección y registros del sensor
DEVICE_ADDRESS = 0x76
REG_TEMP_MSB = 0xFA
REG_TEMP_LSB = 0xFB
REG_TEMP_XLSB = 0xFC
REG_HUM_MSB = 0xFD
REG_HUM_LSB = 0xFE

# Inicializar el bus I2C
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=1000000)

# Modo de operacion del sensor

i2c.writeto_mem(DEVICE_ADDRESS,0xF2,bytes([0x02]))
i2c.writeto_mem(DEVICE_ADDRESS,0xF4,bytes([0x93]))
i2c.writeto_mem(DEVICE_ADDRESS,0xF5,bytes([0x22]))


# Leer los registros de calibración del sensor
calib_data = i2c.readfrom_mem(DEVICE_ADDRESS, 0x88, 24)
calib_x = [
    (calib_data[1] << 8) | calib_data[0],
    (calib_data[3] << 8) | calib_data[2],
    (calib_data[5] << 8) | calib_data[4],
    (calib_data[7] << 8) | calib_data[6],
    (calib_data[9] << 8) | calib_data[8],
    (calib_data[11] << 8) | calib_data[10],
    (calib_data[13] << 8) | calib_data[12],
    (calib_data[15] << 8) | calib_data[14],
    (calib_data[17] << 8) | calib_data[16],
    (calib_data[19] << 8) | calib_data[18],
    (calib_data[21] << 8) | calib_data[20],
    (calib_data[23] << 8) | calib_data[22]
    ]

# Conectar a la red WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Conectando a la red WiFi...")
    wlan.connect(SSID,PASSWORD_WLAN)
    while not wlan.isconnected():
        pass
    print("Conexión WiFi establecida. Dirección IP:", wlan.ifconfig()[0])

def calculos(calib):
    # Leer los registros de temperatura del sensor
    temp_msb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_TEMP_MSB, 1)[0]
    temp_lsb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_TEMP_LSB, 1)[0]
    temp_xlsb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_TEMP_XLSB, 1)[0]

    # Leer los registros de humedad del sensor
    hum_msb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_HUM_MSB, 1)[0]
    hum_lsb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_HUM_LSB, 1)[0]

    # Convertir los valores de los registros en grados Celsius

    adc_T = (temp_msb << 12) | (temp_lsb << 4) | (temp_xlsb >> 4)
    var1 = ((((adc_T >> 3) - (calib[0] << 1))) * (calib[1])) >> 11
    var2 = (((((adc_T >> 4) - (calib[0])) * ((adc_T >> 4) - (calib[0]))) >> 12) * (calib[2])) >> 14
    t_fine = var1 + var2
    temperature = (t_fine * 5 + 128) >> 8

    # Convertir los valores de los registros en humedad relativa (%)

    adc_H = (hum_msb << 8) | hum_lsb
    humidity = ((adc_H / 2**16) * 100)

    return([(temperature/100),humidity])

while True:
    temp = ""
    # Conectar al servidor MQTT y publicar el mensaje
    client = MQTTClient(CLIENT_ID, SERVER, PORT, USER, PASSWORD)
    print("Conectando al servidor MQTT...")
    client.connect()
    for i in range(10):
        print("Espera para enviar dato tiempo",(i+1),"Seg")
        time.sleep(1)
    for i in range(6):
        out_sensor = calculos(calib_x)
        temp = str(out_sensor[0]) + "," + str(round(out_sensor[1],2))
        MESSAGE = temp
        try:
            client.publish(TOPIC, MESSAGE.encode('utf-8'), retain=False, qos=0)
            print("Mensaje MQTT publicado en el tema", TOPIC, "Con los datos:", MESSAGE)
        except OSError:
            print("Error al conectar al servidor MQTT")
        time.sleep(5)

    client.disconnect()
