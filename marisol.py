#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import usb.core, usb.util, usb.control
import crc16
import sys
from collections import OrderedDict
import psycopg2
from datetime import datetime
import configparser

# BOT.INI
config = configparser.ConfigParser()
config.read('/home/pi/ups/bot.ini')
dbkey =  config['PASSDB']['pass']
try:
    connection = psycopg2.connect(user = "pi",
                                  password = dbkey,
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "ups")
    cursor = connection.cursor()
    
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)      

# USB CONNECTION
vendorId = 0x0665
productId = 0x5161
interface = 0
dev = usb.core.find(idVendor=vendorId, idProduct=productId)
if dev.is_kernel_driver_active(interface):
    dev.detach_kernel_driver(interface)
dev.set_interface_altsetting(0,0)

# COMMAND+CRC16
def getCommand(cmd):
    cmd = cmd.encode('utf-8')
    crc = crc16.crc16xmodem(cmd).to_bytes(2,'big')
    cmd = cmd+crc
    cmd = cmd+b'\r'
    while len(cmd)<8:
        cmd = cmd+b'\0'
    return cmd

# SEND COMMAND
def sendCommand(cmd):
    dev.ctrl_transfer(0x21, 0x9, 0x200, 0, cmd)

# RESULT COMMAND
def getResult(timeout=100):
    res=""
    i=0
    while '\r' not in res and i<20:
        try:
            res+="".join([chr(i) for i in dev.read(0x81, 8, timeout) if i!=0x00])
        except usb.core.USBError as e:
            if e.errno == 110:
                pass
            else:
                raise
        i+=1
    return res

# ADD HEADERS
def parseQPIGS(a):
    a = a.split()
    d = {'grid voltage':a[0][1:]+'v', 'grid frequency':a[1]+'hz', 'ac output voltage':a[2]+'v', 
        'ac output frequency':a[3]+'hz', 'ac output aparent power':a[4]+'va', 'ac output active power':a[5]+'w',
         'output load percent':a[6]+'%', 'bus voltage':a[7]+'v', 'battery voltage':a[8]+'v', 
         'battery chraging current':a[9]+'%', 'battery capacity':a[10]+'%', 'inverter head sync temperature':a[11]+'c',
          'pv input current for battery':a[12]+'a', 'pv input voltage ':a[13]+'v', 'battery voltage from scc':a[14]+'v',
           'battery discharge current':a[15]+'a', 'device status':a[16]}
    return json.dumps(d, indent=2)
    
# SQL
def sql_bbdd(sql):
   
    sql.replace(",", ".")
    a = sql.split()
    d = {'grid voltage':a[0][1:]+'v', 'grid frequency':a[1]+'hz', 'ac output voltage':a[2]+'v', 
        'ac output frequency':a[3]+'hz', 'ac output aparent power':a[4]+'va', 'ac output active power':a[5]+'w',
         'output load percent':a[6]+'%', 'bus voltage':a[7]+'v', 'battery voltage':a[8]+'v', 
         'battery chraging current':a[9]+'%', 'battery capacity':a[10]+'%', 'inverter head sync temperature':a[11]+'c',
          'pv input current for battery':a[12]+'a', 'pv input voltage ':a[13]+'v', 'battery voltage from scc':a[14]+'v',
           'battery discharge current':a[15]+'a', 'device status':a[16]}
    
    print(d)
    
    record_to_insert = (float(a[0][1:]) , float(a[1]) ,float(a[2]) , float(a[3]) , int(float(a[4])) , int(float(a[5])) , int(float(a[6])) , int(float(a[7])) , float(a[8]) , int(float(a[9])), int(float(a[10])), int(float(a[11])), int(float(a[12])), float(a[13]), float(a[14]), int(float(a[15])), a[16])
    
    postgres_insert_query = """ INSERT INTO datos (grid_voltage , grid_frequency , ac_output_voltage ,
                                ac_output_frequency , ac_output_aparent_power , ac_output_active_power , 
                                output_load_percent , bus_voltage, battery_voltage, battery_chraging_current,
                                battery_capacity, inverter_head_sync_temperature, pv_input_current_for_battery,
                                pv_input_voltage , battery_voltage_from_scc, battery_discharge_current, 
                                device_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                %s,%s,%s)"""
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    count = cursor.rowcount
    return count, "Record inserted successfully into mobile table"
    
# RUN
res = ""
while res == "":
     sendCommand(getCommand("QPIGS"))
     res = getResult()
     
if res:
    sql_bbdd(res)
      
