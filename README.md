# Marisol
## TelegramBot for AXPERT/etc solar inverter monitoring on a RPi

This scripts communicates a RPi with an AXPERT solar inverter, stores in an a postgresql database and displays it via Grafana  and Telegram Bot.

For install : 
  * `pip3 install --user -r requirements.txt` 
  * In a psql terminal run  `\i ./creartabla.sql`
  * [Install grafana](http://pdacontroles.com/instalacion-completa-dashboard-grafana-en-raspberry-pi-3-b-b/)
  * `cp bot.ini.example bot.ini` 
  * create telegram api key , openweather apikey , and a grafana api key via web interface and fill bot.ini 
  
This scripts are based on [previous work of Dolf Andringa](http://allican.be/blog/2017/01/28/reverse-engineering-cypress-serial-usb.html).We stand on the shoulders of giants :muscle: :metal:


