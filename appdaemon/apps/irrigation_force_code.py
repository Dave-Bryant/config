import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Home Irrigation Force
#
<<<<<<< HEAD
#
=======
#                             THIS HASNT BEEN TESTED
>>>>>>> f587c86160bcb35daa63b0d9c7b664551d9fee37

class Home_Irrigation_Force(hass.Hass):
  def initialize(self):
     self.log("Starting Home Irrigation Force")
     self.listen_state(self.schedule_the_force, "input_boolean.force_irrigation", new = "on")

  def schedule_the_force(self, entity, attribute, old, new, kwargs):
     self.log("FORCE started")
     self.run_in(self.turn_it_off, 3)
     self.call_service("smart_irrigation/smart_irrigation_enable_force_mode")
<<<<<<< HEAD
     self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
     self.call_service("smart_irrigation/smart_irrigation_calculate_daily_adjusted_run_time")
     self.log("FORCE completed ie bucket reset, daily adjusted run time calculated and force set")
=======
     self.log("FORCE completed")
>>>>>>> f587c86160bcb35daa63b0d9c7b664551d9fee37

  def turn_it_off(self,kwargs):
      self.turn_off("input_boolean.force_irrigation")
