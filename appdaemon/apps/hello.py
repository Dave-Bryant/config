import appdaemon.plugins.hass.hassapi as hass
#import datetime

import pymysql.cursors
import sqlite3
import os
import json
from datetime import datetime
from datetime import timedelta
from statistics import mean
import pytz

# Hellow World App
#
# Args:
#


class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")
     #self.log(self.list_services(namespace="global"))
     #self.irrigation_entity = self.get_entity("sensor.smart_irrigation_garden")
     #self.irrigation_entity.call_service("smart_irrigation/reset_bucket")
     #self.call_service("smart_irrigation/reset_bucket", entityid = "sensor.smart_irrigation_garden")
     self.log("Reset complete")


     #self.run_every(self.main_routine,"now", 15)
     
     #self.run_daily(self.main_routine, "9:00:00")


   # testing

   ####################################################################

  # def Check_Kilometers(self, kms, limit, multiple): # odometer, Percent tolerance , distance before notice
  #   kms = str(round(kms/multiple,2)).split('.', 1)[1]
  #   if int(kms) >= 100-limit:
  #       return True
  #   else:
  #       return False



  # def main_routine(self, *args):
  #   self.x = 18238
  #   tyre_check_switch = False
    

  #   if tyre_check_switch and self.Check_Kilometers(self.x, 10, 10000):
  #     print ("get tyres checked")
  #   if not tyre_check_switch and not self.Check_Kilometers(self.x, 10, 10000):
  #     tyre_check_switch = True
  #     print("turned switch on")



    
    #self.garden_running_time = float(self.get_state('input_number.garden_watering_time'))
    #if not self.garden_run: self.log(self.garden_running_time)

    #self.log(self.render_template("{{ states('sensor.smart_irrigation_hourly_adjusted_run_time_2') }}"))

    #state = self.get_state("sensor.smart_irrigation_hourly_adjusted_run_time_2")
    # self.log(self.get_state('sensor.smart_irrigation_base_schedule_index'))
    # if self.get_state('sun.sun') == 'above_horizon': self.log("Works......")
    #
    # if float(self.get_state("sensor.smart_irrigation_hourly_adjusted_run_time")) > 360: self.log("Works......")



    #self.select_option("input_select.irrigation_status", "Irrigation has completed")

    #x = self.get_state('sensor.smart_irrigation_daily_adjusted_run_time')
    #self.set_state('sensor.smart_irrigation_daily_adjusted_run_time', state = x, attribute = {'force_mode_duration': 15})
    #self.set_value("input_number.garden_watering_time",self.cumulative_total) # store
    #self.log("Hello from main main_routine")
