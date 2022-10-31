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


     self.run_in(self.main_routine, 0)
     self.garden_run = False


   # testing

  def is_dst(self, when):
    '''Given the name of Timezone will attempt determine if that timezone is in Daylight Saving Time now (DST)'''
    return when.dst() != timedelta(0)


  def main_routine(self, *args):
     #self.turn_on(entity_id='light.tz3000_tqlv4ug4_ts0001_light')
     #self.get_state(entity_id="sensor.speedtest_ping")
     #self.call_service("homeassistant/update_entity", entity_id = "sensor.speedtest_ping")
     # self.call_service("tts/google_translate_say",
     #                    entity_id = "media_player.study_display",
     #                    message = "Your attention please, internet power cycle in 30 seconds!"
     #                     )

     #################################################
     # Test cases
     #################################################

     # DST in Australia ends April 3, 2022 at 2 am
     self.timezone_eastern = 'Australia/Sydney'
     self.datetime_dst_eastern = pytz.timezone(self.timezone_eastern).localize(datetime(year=2022, month=10, day=5))
     self.datetime_non_dst_eastern = pytz.timezone(self.timezone_eastern).localize(datetime(year=2022, month=4, day=4))
     self.x = self.datetime_dst_eastern.strftime('%y-%m-%d %a %H:%M:%S')
     self.y = self.datetime_non_dst_eastern.strftime('%y-%m-%d %a %H:%M:%S')
     self.log(f'{self.timezone_eastern} {self.x} is in dst: { self.is_dst(self.datetime_dst_eastern)} should be: True')
     self.log(f'{self.timezone_eastern} {self.y} is in dst: {self.is_dst(self.datetime_non_dst_eastern)} should be: False')

     self.config["global_DST_Switch"] = self.is_dst(pytz.timezone('Australia/Sydney').localize(datetime.now()))

     self.log(self.config["global_DST_Switch"])

     self.nowtime = datetime.now()
     self.target = self.nowtime.replace(hour=17, minute=50, second=0, microsecond=0)
     if self.nowtime == self.target: self.log('quit')
     #quit()



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
