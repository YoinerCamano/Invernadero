import machine
import time

# Definir las constantes para la dirección y registro del sensor
DEVICE_ADDRESS = 0x76
REG_TEMP_MSB = 0xFA
REG_TEMP_LSB = 0xFB
REG_TEMP_XLSB = 0xFC
REG_HUM_MSB = 0xFD
REG_HUM_LSB = 0xFE
REG_HUM_XLSB = 0xFF
REG_PRESS_MSB = 0xF7
REG_PRESS_LSB = 0xF8
REG_PRESS_XLSB = 0xF9

MODE_PRES_HIGHRES = 0x34
MODE_TEMP_STANDARD = 0x2E

# Inicializar el bus I2C
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))

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

    # Leer los registros de presión del sensor
    press_msb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_PRESS_MSB, 1)[0]
    press_lsb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_PRESS_LSB, 1)[0]
    press_xlsb = i2c.readfrom_mem(DEVICE_ADDRESS, REG_PRESS_XLSB, 1)[0]

    # Convertir los valores de los registros en grados Celsius
    adc_T = (temp_msb << 12) | (temp_lsb << 4) | (temp_xlsb >> 4)
    var1 = ((((adc_T >> 3) - (calib[0] << 1))) * (calib[1])) >> 11
    var2 = (((((adc_T >> 4) - (calib[0])) * ((adc_T >> 4) - (calib[0]))) >> 12) * (calib[2])) >> 14
    t_fine = var1 + var2
    temperature = (t_fine * 5 + 128) >> 8

    #Convertir los valores de los registros en presión (Pa)

    adc_P = (press_msb << 12) | (press_lsb << 4) | (press_xlsb >> 4)
    var1 = ((temperature) >> 1) - 64000
    var2 = (((var1 >> 2) * (var1 >> 2)) >> 11) * int(calib[5])
    var2 = var2 + ((var1 * int(calib[4])) << 1)
    var2 = (var2 >> 2) + (int(calib[3]) << 16)
    var1 = (((calib[2] * (((var1 >> 2) * (var1 >> 2)) >> 13)) >> 3) + ((calib[1] * var1) >> 1)) >> 18
    var1 = ((32768 + var1) * int(calib[0])) >> 15
    pressure = 0
    if var1 != 0:
        pressure = ((1048576 - adc_P) - (var2 >> 12)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure << 1) // var1
        else:
            pressure = (pressure // var1) * 2
        var1 = (int(calib[8]) * (((pressure >> 3) * (pressure >> 3)) >> 13)) >> 12
        var2 = ((pressure >> 2) * int(calib[7])) >> 13
        pressure = pressure + ((var1 + var2 + int(calib[6])) >> 4)

    # Convertir los valores de los registros en humedad relativa (%)
    adc_H = (hum_msb << 8) | hum_lsb
    humidity = ((adc_H / 2**16) * 100)

    return([(temperature/100),pressure,humidity])

# Imprimir el valor de temperatura en grados Celsius
while True:
    print(calculos(calib_x))
    time.sleep(1)
