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

   # testing

  def main_routine(self, *args):

<<<<<<< HEAD
     #self.log(self.render_template("{{ states('sensor.smart_irrigation_hourly_adjusted_run_time_2') }}"))

     #state = self.get_state("sensor.smart_irrigation_hourly_adjusted_run_time_2")
     self.log(self.get_state('sensor.smart_irrigation_base_schedule_index'))
     if self.get_state('sun.sun') == 'above_horizon': self.log("Works......")

     if float(self.get_state("sensor.smart_irrigation_hourly_adjusted_run_time_2")) > 360: self.log("Works......")

      #self.select_option("input_select.irrigation_status", "Irrigation has completed")
=======
>>>>>>> f587c86160bcb35daa63b0d9c7b664551d9fee37

      #x = self.get_state('sensor.smart_irrigation_daily_adjusted_run_time')
      #self.set_state('sensor.smart_irrigation_daily_adjusted_run_time', state = x, attribute = {'force_mode_duration': 15})
      #self.set_value("input_number.garden_watering_time",self.cumulative_total) # store
     self.log("Hello from main main_routine")
