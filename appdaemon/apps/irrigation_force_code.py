import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Home Irrigation Force
#
# Args: Time or blank
#                             THIS DOESNT WORK

class Home_Irrigation_Force(hass.Hass):
  def initialize(self):
     self.log("Starting Home Irrigation Force")
     self.start_time = self.args["FORCE_TIME"]
     self.listen_state(self.schedule_the_force, "input_boolean.force_irrigation", new = "on")

  def schedule_the_force(self, entity, attribute, old, new, kwargs):
     self.log("FORCE scheduled")
     self.run_in(self.turn_it_off, 3)
     self.run_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")
     if self.start_time != '': self.run_once(self.main_routine, self.start_time)

     # self.run_in(self.main_routine, 0)
  def main_routine(self, *args):

      if  self.run_time < self.render_template("{{states('sensor.smart_irrigation_base_schedule_index') | int}}"):
          self.call_service("smart_irrigation/smart_irrigation_enable_force_mode")
          self.run_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")
          self.log(f"FORCED daily_adjusted_run_time to: {self.run_time} secs")
      else:
          self.log("FORCE not required")

  def turn_it_off(self,kwargs):
      self.turn_off("input_boolean.force_irrigation")
