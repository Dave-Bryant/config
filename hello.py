import appdaemon.plugins.hass.hassapi as hass
#import datetime

# import pymysql.cursors
# import sqlite3
# import os
# import json
from datetime import datetime
from datetime import timedelta
from statistics import mean
import pytz

from influxdb import InfluxDBClient
import math
from eto import ETo, datasets
import pandas as pd


# Hellow World App
#
# Args: xxxxX
#






  
class HelloWorld(hass.Hass):
    def initialize(self):
        self.log("Hello from AppDaemon")
        
    #     self.listen_state(self.toggle_handler, "input_boolean.auto_irrigation_switch")

    # def toggle_handler(self, entity, attribute, old, new, kwargs):
    #     self.log(f"{entity} changed from {old} to {new}")


    #  ET= 4.5
    #  ET_calc= 4.25
    #  apply_rain= 0.5
    #  self.log(f'New ET {ET:0.2f} after ET_calc {ET_calc:0.2f} reduced by Rain bucket {(ET-ET_calc):0.2f} amount')
     #self.log(self.list_services(namespace="default"))
     #self.irrigation_entity = self.get_entity("sensor.smart_irrigation_garden")
     #self.irrigation_entity.call_service("smart_irrigation/reset_bucket")
     #self.call_service("smart_irrigation/reset_all_buckets") 
     #self.call_service("smart_irrigation/set_bucket", entityid = "sensor.smart_irrigation_garden", data = 2 )
     # self.log("Reset complete")

     # self.run_every(self.main_routine,"now", 15)


     # Read Soil Moisture

     # try:
     #    self.soil_moisture = float(self.get_state('sensor.soil_sensor_1_soil_moisture'))
     # except:
     #    self.soil_moisture = 30  # set it to be ignored
     #    self.log("Soil Moisture Batteries are low or flat")
     #self.log(self.list_services(namespace="global"))
     #self.call_service("notify/mobile_app_david_bryants_iphone",message = 'Soil Moisture Batteries are low')
     
     
         
     # if float(self.get_state('sensor.soil_sensor_1_battery')) < 20 or self.get_state('sensor.soil_sensor_1_soil_moisture') == 'unavailable':
     #    self.soil_moisture = 30  # set it to be ignored
     #    self.log("Soil Moisture Batteries are low or flat")
     # else:
     #    self.soil_moisture = float(self.get_state('sensor.soil_sensor_1_soil_moisture'))
         
            
     
        self.run_in(self.main_routine, 0)    

  
    def main_routine(self, *args):
        self.log("Here from AppDaemon?????") 
        #self.select_option("input_select.irrigation_status", "Normal")
        # if self.get_state("input_boolean.auto_master_switch") == "off": self.log("switch is off")
        # else: self.log("switch is on")
        # self.soil_moisture_text = "Soil Moisture too high: " + str(self.get_state("sensor.soil_sensor_1_soil_moisture")) + "%"  
        #print(self.soil_moisture_text)
        # self.state = self.get_state("input_boolean.auto_irrigation_switch")
        
        # if self.state == "on":
        #     self.log("Auto irrigation is enabled, proceeding with action.")
        # elif self.state is None:
        #     self.log("Warning: input_boolean.auto_irrigation_switch not found.")
        self.log("Bye from AppDaemon") 
    
  