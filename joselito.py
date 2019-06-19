#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import requests
import glob 
import os
import pyowm
import configparser

# PASSWORDS
config = configparser.ConfigParser()
config.read('/home/pi/ups/bot.ini')
apigrafana = config['APIGRAFANA']['auth_token']
apiweather = config['APIWEATHER']['api_owm']
dbkey = config['PASSDB']['pass']
telegramkey = config['KEYS']['bot_api']
     
# DB CONECCTION
cur =  psycopg2.connect(database='ups', user='pi', password=dbkey, host='localhost').cursor()

# LOG
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# REQUESTS HEADERS
hed = {'Authorization': 'Bearer ' + apigrafana}

# OPENWEATHERMAPS
def forecast ():  
    owm = pyowm.OWM(apiweather)
    observation = owm.three_hours_forecast("Madrid,ES")
    w = observation.get_forecast()
    nubes = []
    for weather in w:
        nubes.append(weather.get_clouds())
    return nubes

# PSQL QUERY
def bbddcall(cur,query):
     cur.execute(query)
     resultado= [row[0] for row in cur.fetchall()]
     return resultado[0]

def bbddselect(columna):
     return "select "+columna+" from datos order by id desc limit 1;"

# BOT TELEGRAM
def start(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Hola! Soy MariSol, la robota que te informa sobre el estado de la instalación Solar Eléctrica en la EKO. /red para ver el estado actual y las gráficas de la red eléctrica. /paneles para ver el estado actual y las gráficas de los paneles solares. /baterias para ver el estado actual de las baterías y sis gráficas. /graficasayer para ver las gráficas de ayer')

def sol(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text=str(forecast()))
    print(forecast())

def ac(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=10&width=1000&height=500&tz=Europe%2FMadrid', headersss=hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficaac = max(list_of_files, key=os.path.getctime)
    bot.send_message(chat_id=update.message.chat_id, text='El voltaje de la corriente alterna en la red eléctrica es de ' + str(float(bbddcall(cur,bbddselect('ac_output_voltage')))) +'V y la corriente alterna actualmente tiene activos ' + str(int(bbddcall(cur,bbddselect('ac_output_aparent_power')))) +'W')
    bot.send_message(chat_id=update.message.chat_id, text='Las gráficas del día hasta el momento son:')
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficaac, 'rb'))
    print("Peticion AC")

def info(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='<i>BATERIAS</i>\n<b> EN CARGA</b>  🔋         ' + str(int(bbddcall(cur,bbddselect('battery_capacity')))) +'% \n <b>EN DESCARGA</b>  🛢     ' + str(int(bbddcall(cur,bbddselect('battery_chraging_current')))) +'%\n(el porcentaje correcto siempre es el más alto) \n\n<i>RED ELECTRICA</i>\n <b>VOLTAJE </b> ⚡  ' + str(float(bbddcall(cur,bbddselect('ac_output_voltage')))) +'V \n <b>VATIOS</b>  🔌     ' + str(int(bbddcall(cur,bbddselect('ac_output_aparent_power')))) +'W\n\n<i>INVERSOR</i> \n<b>TEMPERATURA</b>  🌡️     ' + str(int(bbddcall(cur,bbddselect('inverter_head_sync_temperature')))) +' °C', parse_mode=telegram.ParseMode.HTML)
    print("Peticion AC")

def pv(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=8&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficapaneles = max(list_of_files, key=os.path.getctime)
    bot.send_message(chat_id=update.message.chat_id, text='La entrada de voltaje en las placas solares es de ' + str(float(bbddcall(cur,bbddselect('pv_input_voltage'))))+'V y el amperaje de entrada de las placas en las baterías es de ' + str(float(bbddcall(cur,bbddselect('pv_input_current_for_battery')))) +'A') 
    bot.send_message(chat_id=update.message.chat_id, text='Las gráficas del día hasta el momento son:')
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficapaneles, 'rb'))
    print("Peticion PV")

def battery(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=20&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficabaterias = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=22&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficabaterias2 = max(list_of_files, key=os.path.getctime)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficabaterias, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficabaterias2, 'rb'))

    print("Peticion Bateria")

def graficasayer(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=17&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficaacayer = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=16&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficabateriasayer = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=18&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficapanelesayer = max(list_of_files, key=os.path.getctime)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficaacayer, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficabateriasayer, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficapanelesayer, 'rb'))

def graficashoy(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=10&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficaachoy = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=8&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficabateriashoy = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=12&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficapaneleshoy = max(list_of_files, key=os.path.getctime)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficaachoy, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficabateriashoy, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficapaneleshoy, 'rb'))

def graficas3horas(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=13&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficaac3horas = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=15&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficabaterias3horas = max(list_of_files, key=os.path.getctime)
    requests.get('http://127.0.0.1:3000/render/d-solo/sUy3R3WRk/marisol-eko-panel-solar?orgId=1&panelId=14&width=1000&height=500&tz=Europe%2FMadrid', headers = hed)
    list_of_files = glob.glob('/var/lib/grafana/png/*')
    graficapaneles3horas = max(list_of_files, key=os.path.getctime)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficaac3horas, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficabaterias3horas, 'rb'))
    bot.send_photo(chat_id=update.message.chat_id, photo=open(graficapaneles3horas, 'rb'))

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def error(bot, update):
    logger.warning('Update "%s" caused error "%s"', bot, update.error)

def main():
    updater = Updater(telegramkey)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("red", ac))
    dp.add_handler(CommandHandler("paneles", pv))
    dp.add_handler(CommandHandler("baterias", battery))
    dp.add_handler(CommandHandler("graficasayer", graficasayer))
    dp.add_handler(CommandHandler("graficashoy", graficashoy))
    dp.add_handler(CommandHandler("graficas3horas", graficas3horas))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("tiempo", sol))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
