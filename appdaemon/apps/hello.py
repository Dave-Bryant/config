import appdaemon.plugins.hass.hassapi as hass
#import datetime

import pymysql.cursors
import sqlite3
import os
import json
from datetime import datetime
from datetime import timedelta
from statistics import mean

# Hellow World App
#
# Args:
#


class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")


     self.run_in(self.main_routine, 0)
     self.garden_run = False

   # testing

  def main_routine(self, *args):

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
     self.log("Hello from main main_routine")
