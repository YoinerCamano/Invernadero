from machine import SoftI2C, Pin
import time

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
    x= calculos(calib_x)
    print("Actualmente la temperatura es " + str(x[0]) + "°C")
    time.sleep(5)
