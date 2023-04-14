from machine import SoftI2C, Pin
import urequests as requests
from umqtt.simple import MQTTClient
import time, network, json

# Configuración de la red WiFi
SSID = "MOTO G"
PASSWORD_WLAN = "2017219010"

# Configuración de la conexión MQTT
SERVER = "44.200.222.162"
PORT = 1883
USER = "guest"
PASSWORD = "guest"
CLIENT_ID = "Sensor_Esp32"
TOPIC = b'mensajes'

# Configuración BOT TELEGRAM
bot_token = "5839981812:AAH7AUgJNLoeo1E2LsZqb2ay8uGe4ecwE_I"
chat_id = "1214775886"

TEMP_MAX_PERMITIDA = 40
TEMP_MIN_PERMITIDA = 30
HUM_MAX_PERMITIDA = 40
HUM_MIN_PERMITIDA = 35

temp_max  = 0
temp_min = 50
hum_max = 0
hum_min = 100

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
    for i in range(6):
        out_sensor = calculos(calib_x)
        if out_sensor[0] >= temp_max:
            temp_max = out_sensor[0]

        if out_sensor[0] <= temp_min:
            temp_min = out_sensor[0]

        if out_sensor[1] >= hum_max:
            hum_max = out_sensor[1]

        if out_sensor[1] <= hum_min:
            hum_min = out_sensor[1]
        print("Temperatura actual:" + str(out_sensor[0]) + "°C Humedad actual:" + str(out_sensor[1]) + "%, temperatura maxima:" + str(temp_max) + "°C, temperatura minima:" + str(temp_min) + " °C, humedad max:" + str(hum_max) + "%, humedad minima:" + str(hum_min)+ "%")
        time.sleep(1)

