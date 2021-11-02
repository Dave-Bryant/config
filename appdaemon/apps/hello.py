import appdaemon.plugins.hass.hassapi as hass
import datetime

# Hellow World App
#
# Args:
#


class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")

     self.run_in(self.main_routine, 0)

  def main_routine(self, *args):
      #x = self.get_state('sensor.smart_irrigation_daily_adjusted_run_time')
      #self.set_state('sensor.smart_irrigation_daily_adjusted_run_time', state = x, attribute = {'force_mode_duration': 15})
      #self.set_value("input_number.garden_watering_time",self.cumulative_total) # store
      self.log("Hello from main main_routine")
