import telebot
from influxdb_client import InfluxDBClient

influx_bucket = 'rabbit'
influx_token = 'token-secreto'
influx_org = 'org'
influx_url = 'http://localhost:8086'


TOKEN = '5839981812:AAH7AUgJNLoeo1E2LsZqb2ay8uGe4ecwE_I'
bot = telebot.TeleBot(TOKEN)    

Clientes_telegram = {1:1214775886,2:1297126833}


def obtener_datos_databases(datos):
    for record in datos:
        data = record.get_value()
    return data

def consultar_databases(selection_data):
    client = InfluxDBClient(url=influx_url, token=influx_token)
    # Consultar los datos más recientes en el bucket
    query = 'from(bucket:"{0}") |> range(start: -5m)'.format(influx_bucket)
    result = client.query_api().query(query, org=influx_org)
    # Imprimir los resultados
    if selection_data == "humedad_actual":
        selection =  result[0]
    if selection_data == "humedad_maxima":
        selection = result[1]
    if selection_data == "humedad_minima":
        selection = result[2]
    if selection_data == "temperatura_actual":
        selection = result[4]
    if selection_data == "temperatura_maxima":
        selection = result[5]
    if selection_data == "temperatura_minima":
        selection = result[6]

    return (obtener_datos_databases(selection))

def aprobacion(usuario,clientes):
    passing = False
    for i in clientes:
        if clientes[i] == usuario:
            passing= True 
    return passing

def message_desaprobacion(cliente_id,username):
        instrucciones = "Bienvenido {}!\n Lamentablemente no tienes un invernadero con nosotros, Esperamos que pronto des el salto que necesita tu cultivo\n".format(username)
        bot.send_message(cliente_id,instrucciones)
    


@bot.message_handler(commands=['start', 'help'])
def enviar_instrucciones(message):
    instrucciones = "Bienvenido {}!\n Puedes usar los siguientes comandos:\n\n"\
                    "/Temperatura_Actual - Ver la temperatura actual\n" \
                    "/Temperatura_Maxima - Ver la temperatura maxima\n" \
                    "/Temperatura_Minima - Ver la temperatura minima\n" \
                    "/Humedad_Actual - Ver la temperatura actual\n" \
                    "/Humedad_Maxima - Ver la temperatura maxima\n" \
                    "/Humedad_Minima - Ver la humedad actual".format(message.from_user.username)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, instrucciones)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)


@bot.message_handler(commands=['Temperatura_Actual'])
def mostrar_temperatura(message):
    data = consultar_databases("temperatura_actual")
    mensaje = "La temperatura actual es: {} grados Celsius".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)

@bot.message_handler(commands=['Temperatura_Maxima'])
def mostrar_temperatura(message):
    data = consultar_databases("temperatura_maxima")
    mensaje = "La temperatura Maxima es: {} grados Celsius".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)

@bot.message_handler(commands=['Temperatura_Minima'])
def mostrar_temperatura(message):
    data = consultar_databases("temperatura_minima")
    mensaje = "La temperatura Minima es: {} grados Celsius".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)

@bot.message_handler(commands=['Humedad_Actual'])
def mostrar_humedad(message):
    data = consultar_databases("humedad_actual")
    mensaje = "La humedad actual es: {}%".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)

@bot.message_handler(commands=['Humedad_Maxima'])
def mostrar_humedad(message):
    data = consultar_databases("humedad_maxima")
    mensaje = "La humedad maxima es: {}%".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)

@bot.message_handler(commands=['Humedad_Minima'])
def mostrar_humedad(message):
    data = consultar_databases("humedad_minima")
    mensaje = "La humedad Minima es: {}%".format(data)
    if aprobacion(message.chat.id,Clientes_telegram):
        bot.send_message(message.chat.id, mensaje)
    else: 
        message_desaprobacion(message.chat.id,message.from_user.username)


bot.polling()