from machine import SoftI2C, Pin
import time

BMP280_ADDR = 0x76
# Inicializar el bus I2C

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)

# Escribir el comando de configuración de resolución de temperatura

i2c.writeto(BMP280_ADDR, bytes([0xF4, 0x4B]))  # 0x27 es una resolución de 12 bits

while True:
    i2c.writeto(BMP280_ADDR, bytes([0xFA , 0xFB, 0xFC]))
    print(i2c.readfrom(BMP280_ADDR,9)[0])
    time.sleep(2)
